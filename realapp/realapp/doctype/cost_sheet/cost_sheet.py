# Copyright (c) 2025
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

ROW_DTYPE = "Cost Sheet Payment Schedule"

class CostSheet(Document):
    def validate(self):
        self._pull_unit_snapshot()
        self._apply_type_rules()
        self._ensure_payment_scheme_rows()
        self._compute_header_values()
        self._compute_before_registration()
        self._compute_grand_total()

    # -------- core pulls / rules --------

    def _pull_unit_snapshot(self):
        if not self.unit:
            frappe.throw("Please select a Unit.")

        u = frappe.get_doc("Unit", self.unit)

        # Always mirror these identifiers from Unit
        self.project = u.project
        self.block = u.block
        self.floor_number = u.floor_number
        self.salable_area = u.salable_area

        # This value (excl base) is the anchor for Negotiated math
        self.value_excluding_bp = u.value_excluding_bp

        # Keep a tiny context for later use
        self._unit_ctx = frappe._dict(
            base=u.basic_price_per_sft,
            ex_bp=u.value_excluding_bp,
            full_unit_value=u.full_unit_value
        )

    def _apply_type_rules(self):
        """Standard -> lock base to Unit; Negotiated -> keep user's base."""
        if self.cost_sheet_type == "Standard":
            self.basic_price_per_sft = self._unit_ctx.base or 0.0
        elif not self.basic_price_per_sft:
            # Negotiated but empty -> fall back to Unit to avoid zeroing
            self.basic_price_per_sft = self._unit_ctx.base or 0.0

    def _ensure_payment_scheme_rows(self):
        """If a template is chosen and no rows exist, populate once."""
        if self.payment_scheme_template and not (self.payment_schedule or []):
            rows = get_payment_scheme_rows(self.payment_scheme_template)
            for r in rows:
                self.append("payment_schedule", {
                    "scheme_code": r.scheme_code,
                    "milestone": r.milestone,
                    "particulars": r.particulars,
                    "percentage": r.percentage,
                })

    # -------- calculations --------

    def _compute_header_values(self):
        """Recompute AOS, taxes & net based on base + ex_bp + settings."""
        area = flt(self.salable_area)
        base = flt(self.basic_price_per_sft)
        ex_bp = flt(self.value_excluding_bp)

        if area <= 0:
            self.aos_value = 0
            self.aos_gst = 0
            self.aos_value_gst = 0
            self.tds_amount = 0
            self.net_payable = 0
            self.effective_rate_per_sft = 0
            self.full_unit_value = 0
            self._spread_schedule_amounts(0)
            return

        # Settings are the single source for tax rates
        settings = frappe.get_single("Realapp Settings")
        gst_rate = flt(settings.gst_rate or 5)
        tds_rate = flt(settings.tds_rate or 1)

        # Full Unit Value (info) mirrors Unit rule (no amenities/infra):
        # area * (base + rise + facing + corner) + car_park
        # We only have the Unit's computed one safely, so recompute from Unit ctx when available.
        # If not available, fall back to AOS + ex_bp approximation.
        self.full_unit_value = flt(self._unit_ctx.full_unit_value or (base * area + ex_bp), 2)

        # AOS core
        self.aos_value = flt(base * area + ex_bp, 2)

        # Taxes
        self.aos_gst = flt(self.aos_value * gst_rate / 100.0, 2)
        self.aos_value_gst = flt(self.aos_value + self.aos_gst, 2)
        self.tds_amount = flt(self.aos_value * tds_rate / 100.0, 2)

        # Net & effective
        self.net_payable = flt(self.aos_value_gst - self.tds_amount, 2)
        self.effective_rate_per_sft = flt(self.net_payable / area, 2)

        # Spread amounts on schedule
        self._spread_schedule_amounts(self.aos_value)

    def _spread_schedule_amounts(self, aos_value: float):
        for d in self.get("payment_schedule", []):
            d.amount = flt(aos_value * flt(d.percentage) / 100.0, 2)

    def _compute_before_registration(self):
        """Compute read-only 'Before Registration' section from Settings."""
        s = frappe.get_single("Realapp Settings")
        area = flt(self.salable_area)

        maint_rate = flt(s.maintenance_rate_per_sft)
        maint_gst_rate = flt(s.maintenance_gst_rate or 18)
        corpus_rate = flt(s.corpus_fund_rate_per_sft)
        move_in = flt(s.move_in_charges)
        rcd = flt(s.refundable_caution_deposit)
        regn = flt(s.default_registration_charges)

        maintenance_charges = flt(maint_rate * area, 2)
        maintenance_gst = flt(maintenance_charges * maint_gst_rate / 100.0, 2)
        corpus_fund = flt(corpus_rate * area, 2)

        total = flt(maintenance_charges + maintenance_gst + corpus_fund + move_in + rcd + regn, 2)

        self.maintenance_charges = maintenance_charges
        self.maintenance_gst = maintenance_gst
        self.corpus_fund = corpus_fund
        self.move_in_charges = move_in
        self.refundable_caution_deposit = rcd
        self.registration_charges = regn
        self.before_registration_total = total

    def _compute_grand_total(self):
        self.grand_total_payable = flt(self.aos_value_gst) + flt(self.before_registration_total or 0.0)

# ---------------- Whitelisted helpers for JS ----------------

@frappe.whitelist()
def get_payment_scheme_rows(template: str):
    """Fetch rows from Payment Scheme Template and return them for Cost Sheet."""
    if not template:
        return []

    doc = frappe.get_doc("Payment Scheme Template", template)

    out = []
    for d in doc.get("payment_scheme_detail") or []:  # 👈 correct child table fieldname
        out.append({
            "scheme_code": d.scheme_code,
            "milestone": d.milestone,
            "particulars": d.particulars,
            "percentage": d.percentage
        })
    return out


@frappe.whitelist()
def compute_header_values(base_price_per_sft: float, salable_area: float, value_excluding_bp: float):
    """Server source-of-truth for header math using settings GST/TDS."""
    base = flt(base_price_per_sft)
    area = flt(salable_area)
    ex_bp = flt(value_excluding_bp)

    if area <= 0:
        return frappe._dict(
            full_unit_value=0, aos_value=0, aos_gst=0, aos_value_gst=0,
            tds_amount=0, net_payable=0, effective_rate_per_sft=0
        )

    s = frappe.get_single("Realapp Settings")
    gst_rate = flt(s.gst_rate or 5)
    tds_rate = flt(s.tds_rate or 1)

    aos = flt(base * area + ex_bp, 2)
    aos_gst = flt(aos * gst_rate / 100.0, 2)
    aos_with_gst = flt(aos + aos_gst, 2)
    tds = flt(aos * tds_rate / 100.0, 2)
    net = flt(aos_with_gst - tds, 2)

    return frappe._dict(
        # We can’t recompute Full Unit Value precisely on server without Unit’s rate breakdown;
        # return AOS as a safe placeholder; form will still show Unit’s stored FU value after pull.
        full_unit_value=flt(base * area + ex_bp, 2),
        aos_value=aos,
        aos_gst=aos_gst,
        aos_value_gst=aos_with_gst,
        tds_amount=tds,
        net_payable=net,
        effective_rate_per_sft=flt(net / area, 2)
    )

@frappe.whitelist()
def compute_before_registration(salable_area: float):
    """Stateless compute of 'Before Registration' using Settings."""
    s = frappe.get_single("Realapp Settings")
    area = flt(salable_area)

    maint_rate = flt(s.maintenance_rate_per_sft)
    maint_gst_rate = flt(s.maintenance_gst_rate or 18)
    corpus_rate = flt(s.corpus_fund_rate_per_sft)
    move_in = flt(s.move_in_charges)
    rcd = flt(s.refundable_caution_deposit)
    regn = flt(s.default_registration_charges)

    maintenance_charges = flt(maint_rate * area, 2)
    maintenance_gst = flt(maintenance_charges * maint_gst_rate / 100.0, 2)
    corpus_fund = flt(corpus_rate * area, 2)

    total = flt(maintenance_charges + maintenance_gst + corpus_fund + move_in + rcd + regn, 2)

    return frappe._dict(
        maintenance_charges=maintenance_charges,
        maintenance_gst=maintenance_gst,
        corpus_fund=corpus_fund,
        move_in_charges=move_in,
        refundable_caution_deposit=rcd,
        registration_charges=regn,
        before_registration_total=total
    )
