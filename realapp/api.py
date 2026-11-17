import hashlib
import hmac
import secrets

import frappe
from frappe.rate_limiter import rate_limit
from frappe.utils import add_to_date, cint, get_datetime, get_url, now, now_datetime

def _sender():
    """Site config 'consent_sender' if set, else the Default Outgoing email account."""
    return frappe.conf.get("consent_sender") or frappe.db.get_value(
        "Email Account", {"default_outgoing": 1, "enable_outgoing": 1}, "email_id"
    )
OTP_MINUTES = 10
MAX_ATTEMPTS = 5
RESEND_SECONDS = 60


def _hash(code, salt):
    return hashlib.sha256(f"{code}:{salt}".encode()).hexdigest()


def _find(email):
    email = (email or "").strip().lower()
    if not email:
        return None
    name = frappe.db.get_value("Marketing Consent", {"email": email}, "name")
    return frappe.get_doc("Marketing Consent", name) if name else None


def _check(email, code):
    """Returns the record if the code is valid, else None."""
    doc = _find(email)
    if not doc or not doc.otp_hash or not doc.otp_expiry:
        return None
    if cint(doc.otp_attempts) >= MAX_ATTEMPTS:
        return None
    if get_datetime(doc.otp_expiry) < now_datetime():
        return None
    if not hmac.compare_digest(_hash((code or "").strip(), doc.token), doc.otp_hash):
        doc.db_set("otp_attempts", cint(doc.otp_attempts) + 1, update_modified=False)
        return None
    return doc


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="email", limit=5, seconds=3600)
def send_otp(email=None):
    # Always returns the same result, so nobody can discover who is a customer.
    doc = _find(email)
    if doc and doc.email:
        last = doc.get("otp_sent_on")
        too_soon = last and (now_datetime() - get_datetime(last)).total_seconds() < RESEND_SECONDS
        if not too_soon:
            code = f"{secrets.randbelow(1000000):06d}"
            doc.db_set(
                {
                    "otp_hash": _hash(code, doc.token),
                    "otp_expiry": add_to_date(now_datetime(), minutes=OTP_MINUTES),
                    "otp_attempts": 0,
                    "otp_sent_on": now(),
                },
                update_modified=False,
            )
            try:
                frappe.sendmail(
                    recipients=[doc.email],
                    sender=_sender(),
                    subject="Your Tridasa Realty verification code",
                    message=(
                        f"<p>Dear {doc.customer_name or 'Customer'},</p>"
                        f"<p>Your verification code is:</p>"
                        f"<p style='font-size:26px;letter-spacing:6px;font-weight:700'>{code}</p>"
                        f"<p>It is valid for {OTP_MINUTES} minutes. If you did not ask for it, "
                        f"please ignore this email.</p>"
                        f"<p>Warm regards,<br>Team Tridasa Realty</p>"
                    ),
                    now=True,
                )
            except Exception:
                frappe.log_error(title="Consent OTP email failed")
    return {"ok": True}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="email", limit=20, seconds=3600)
def verify_otp(email=None, code=None):
    doc = _check(email, code)
    if not doc:
        return {"ok": False}
    return {
        "ok": True,
        "name": doc.customer_name or "",
        "c1": cint(doc.phone_calls),
        "c2": cint(doc.call_recording),
        "c3": cint(doc.digital_comms),
        "c4": cint(doc.marketing_comms),
    }


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="email", limit=20, seconds=3600)
def update_preferences(email=None, code=None, c1=0, c2=0, c3=0, c4=0):
    doc = _check(email, code)
    if not doc:
        return {"ok": False}

    had_any = any([doc.phone_calls, doc.call_recording, doc.digital_comms, doc.marketing_comms])

    doc.phone_calls = cint(c1)
    doc.call_recording = cint(c2)
    doc.digital_comms = cint(c3)
    doc.marketing_comms = cint(c4)
    has_any = any([doc.phone_calls, doc.call_recording, doc.digital_comms, doc.marketing_comms])

    doc.status = "Withdrawn" if (had_any and not has_any) else "Responded"
    doc.notice_version = "v1"
    doc.responded_on = now()
    # the code is single-use
    doc.otp_hash = ""
    doc.otp_expiry = None
    doc.otp_attempts = 0
    doc.save(ignore_permissions=True)

    # if doc.email:
    #     link = get_url() + "/update-preferences"
    #     try:
    #         frappe.sendmail(
    #         doc.db_set("thank_you_sent_on", now(), update_modified=False)
    #             recipients=[doc.email],
    #             sender=_sender(),
    #             subject="Your preferences are updated, Tridasa Realty",
    #             message=(
    #                 f"<p>Dear {doc.customer_name or 'Customer'},</p>"
    #                 f"<p>Thank you. We have recorded your updated communication preferences.</p>"
    #                 f"<p>You can change or withdraw your choices at any time at "
    #                 f"<a href='{link}'>this page</a>, by writing to [email] or calling [number].</p>"
    #                 f"<p>Warm regards,<br>Team Tridasa Realty</p>"
    #             ),
    #             now = True,
    #         )
    #     except Exception:
    #         frappe.log_error(title="Consent update email failed")

    return {"ok": True}


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(key="token", limit=30, seconds=3600)
def get_name(token=None):
    row = None
    if token:
        row = frappe.db.get_value(
            "Marketing Consent", {"token": token},
            ["customer_name", "status"], as_dict=True
        )
    if not row:
        return {}
    return {
        "name": row.customer_name or "",
        "done": row.status not in ("Pending", "No Response"),
    }
