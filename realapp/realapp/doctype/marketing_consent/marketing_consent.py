import secrets

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, get_url, now

CHOICES = [
    ("Phone Calls", "phone_calls"),
    ("Call Recording", "call_recording"),
    ("Digital Communication", "digital_comms"),
    ("Marketing Communication", "marketing_comms"),
]


class MarketingConsent(Document):
    def before_insert(self):
        if not self.token:
            self.token = secrets.token_urlsafe(24)
        self.email = (self.email or "").strip().lower()
        if not self.status:
            self.status = "Pending"
        if frappe.db.exists("Marketing Consent", {"email": self.email}):
            frappe.throw(f"A record for {self.email} already exists.")

    def validate(self):
        self.log_consent_history()

    def log_consent_history(self):
        """Add one row per choice each time the customer submits or updates."""
        if not self.responded_on:
            return
        before = self.get_doc_before_save()
        old = before.responded_on if before else None
        if old and get_datetime(old) == get_datetime(self.responded_on):
            return  # no new submission

        existing = self.get("consent_history") or []
        is_update = bool(existing)
        n = len({str(r.changed_on) for r in existing}) + 1
        source = "Preference Update (OTP)" if is_update else "Consent Form (email link)"
        for label, fieldname in CHOICES:
            self.append(
                "consent_history",
                {
                    "consent_type": label,
                    "response": "Yes" if self.get(fieldname) else "No",
                    "changed_on": self.responded_on,
                    "source": source,
                    "response_version": f"v{n}",
                },
            )
        self.flags.send_thank_you = True
        self.flags.is_update = is_update

    def on_update(self):
        if not self.flags.get("send_thank_you") or not self.email:
            return
        self.flags.send_thank_you = False

        from realapp.api import _sender

        link = get_url() + "/update-preferences"
        subject = (
            "Your preferences are updated, Tridasa Realty"
            if self.flags.get("is_update")
            else "Thank you, Tridasa Realty"
        )
        try:
            frappe.sendmail(
                recipients=[self.email],
                sender=_sender(),
                subject=subject,
                message=(
                    f"<p>Dear {self.customer_name or 'Customer'},</p>"
                    "<p>Thank you. We have recorded your communication preferences.</p>"
                    f"<p>You can change or withdraw your choices at any time at "
                    f"<a href='{link}'>this page</a>, by writing to [email] or calling [number].</p>"
                    "<p>Warm regards,<br>Team Tridasa Realty</p>"
                ),
                now=True,
            )
            self.db_set("thank_you_sent_on", now(), update_modified=False)
        except Exception:
            frappe.log_error(title="Consent thank-you email failed")