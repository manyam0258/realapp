# Copyright (c) 2025
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class CostSheet(Document):
    def validate(self):
        self._pull_unit_snapshot()
        self._apply_type_rules()
        self._check_unit_availability()
        self._ensure_payment_schedule_rows()
        self._compute_header_values()
        self._compute_before_registration()
        self._compute_grand_total()

    # -------- core pulls / rules --------

    def _pull_unit_snapshot(self):
        if not self.unit:
            frappe.throw("Please select a Unit.")

        u = frappe.get_doc("Unit", self.unit)

        # Always mirror identifiers from Unit
        self.project = u.project
        self.block = u.block
        self.floor_number = u.floor_number
        self.salable_area = u.salable_area
        self.value_excluding_bp = u.value_excluding_bp

        self._unit_ctx = frappe._dict(
            base=u.basic_price_per_sft,
            ex_bp=u.value_excluding_bp,
            full_unit_value=u.full_unit_value,
            status=u.status
        )

    def _apply_type_rules(self):
        """Standard → lock base to Unit; Negotiated → allow custom base."""
        if self.cost_sheet_type == "Standard":
            self.basic_price_per_sft = self._unit_ctx.base or 0.0
        elif not self.basic_price_per_sft:
            self.basic_price_per_sft = self._unit_ctx.base or 0.0

    def _check_unit_availability(self):
        """Only allow Cost Sheet for Available units."""
        if self._unit_ctx.status in ("Booked", "Blocked", "Sold"):
            frappe.throw(f"Unit {self.unit} is {self._unit_ctx.status} and cannot be sold.")

    def _ensure_payment_schedule_rows(self):
        """Populate payment schedule with scheme + dates if empty."""
        if self.payment_scheme_template and not (self.payment_schedule or []):
            rows = get_payment_scheme_rows(self.payment_scheme_template, self.block)
            for r in rows:
                self.append("payment_schedule", {
                    "scheme_code": r.get("scheme_code"),
                    "milestone": r.get("milestone"),
                    "particulars": r.get("particulars"),
                    "percentage": r.get("percentage"),
                    "milestone_date": r.get("milestone_date"),
                })

    # -------- calculations --------

    def _compute_header_values(self):
        """Recompute AOS, GST, TDS, Net Payable etc."""
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

        settings = frappe.get_single("Realapp Settings")
        gst_rate = flt(settings.gst_rate or 5)
        tds_rate = flt(settings.tds_rate or 1)

        self.full_unit_value = flt(self._unit_ctx.full_unit_value or (base * area + ex_bp), 2)
        self.aos_value = flt(base * area + ex_bp, 2)

        self.aos_gst = flt(self.aos_value * gst_rate / 100.0, 2)
        self.aos_value_gst = flt(self.aos_value + self.aos_gst, 2)
        self.tds_amount = flt(self.aos_value * tds_rate / 100.0, 2)

        self.net_payable = flt(self.aos_value_gst - self.tds_amount, 2)
        self.effective_rate_per_sft = flt(self.net_payable / area, 2)

        self._spread_schedule_amounts(self.aos_value, gst_rate, tds_rate)

    def _spread_schedule_amounts(self, aos_value: float, gst_rate: float = 5, tds_rate: float = 1):
        """Distribute AOS across schedule rows and compute GST, TDS, Net."""
        for d in self.get("payment_schedule", []):
            d.amount = flt(aos_value * flt(d.percentage) / 100.0, 2)
            d.gst_amount = flt(d.amount * gst_rate / 100.0, 2)
            d.tds_amount = flt(d.amount * tds_rate / 100.0, 2)
            d.net_payable = flt(d.amount + d.gst_amount - d.tds_amount, 2)

    def _compute_before_registration(self):
        """Charges before registration."""
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


# ---------------- Whitelisted helpers ----------------

@frappe.whitelist()
def get_payment_scheme_rows(template: str, block: str = None):
    """Fetch Payment Scheme rows and merge with Tower Milestone dates from Block."""
    if not template:
        return []

    doc = frappe.get_doc("Payment Scheme Template", template)

    milestone_dates = {}
    if block:
        block_doc = frappe.get_doc("Block", block)
        for t in block_doc.get("tower_milestones") or []:
            if t.scheme_code:
                milestone_dates[t.scheme_code] = t.milestone_date

    out = []
    for d in doc.get("payment_scheme_details") or []:
        out.append({
            "scheme_code": d.scheme_code,
            "milestone": d.milestone,
            "particulars": d.particulars,
            "percentage": d.percentage,
            "milestone_date": milestone_dates.get(d.scheme_code)
        })
    return out


@frappe.whitelist()
def compute_header_values(base_price_per_sft: float, salable_area: float, value_excluding_bp: float):
    """Server-side truth for AOS/GST/TDS/Net."""
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
    """Stateless compute of 'Before Registration' charges."""
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
