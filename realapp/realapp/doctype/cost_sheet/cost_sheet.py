# Copyright (c) 2025
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc


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

        # Context we reuse later
        self._unit_ctx = frappe._dict(
            base=u.basic_price_per_sft,
            ex_bp=u.value_excluding_bp,
            full_unit_value=u.full_unit_value,
            status=u.status,
        )

    def _apply_type_rules(self):
        """Standard → lock base to Unit; Negotiated → allow custom base (fallback to Unit if empty)."""
        if self.cost_sheet_type == "Standard":
            self.basic_price_per_sft = self._unit_ctx.base or 0.0
        elif not self.basic_price_per_sft:
            self.basic_price_per_sft = self._unit_ctx.base or 0.0

    def _check_unit_availability(self):
        """Only allow Cost Sheet for Available units."""
        if self._unit_ctx.status in ("Booked", "Blocked", "Sold"):
            frappe.throw(f"Unit {self.unit} is {self._unit_ctx.status} and cannot be sold.")

    def _ensure_payment_schedule_rows(self):
        """Populate payment schedule with template rows and tower milestone dates if empty."""
        if self.payment_scheme_template and not (self.payment_schedule or []):
            rows = get_payment_scheme_rows(self.payment_scheme_template, self.block)
            for r in rows:
                self.append("payment_schedule", {
                    "scheme_code": r.get("scheme_code"),
                    "milestone": r.get("milestone"),
                    "milestone_item": r.get("milestone_item"),
                    "particulars": r.get("particulars"),
                    "percentage": r.get("percentage"),
                    "milestone_date": r.get("milestone_date"),
                })

    # -------- calculations --------

    def _compute_header_values(self):
        """Recompute AOS, GST, TDS, Net Payable, Effective rate; then spread into child rows."""
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

        # Full Unit Value mirrors Unit’s formula; fall back to (base*area + ex_bp)
        self.full_unit_value = flt(self._unit_ctx.full_unit_value or (base * area + ex_bp), 2)

        # AOS (Agreement of Sale) core
        self.aos_value = flt(base * area + ex_bp, 2)

        # Taxes
        self.aos_gst = flt(self.aos_value * gst_rate / 100.0, 2)
        self.aos_value_gst = flt(self.aos_value + self.aos_gst, 2)
        self.tds_amount = flt(self.aos_value * tds_rate / 100.0, 2)

        # Net & Effective
        self.net_payable = flt(self.aos_value_gst - self.tds_amount, 2)
        self.effective_rate_per_sft = flt(self.net_payable / area, 2)

        # Spread into schedule rows
        self._spread_schedule_amounts(self.aos_value, gst_rate, tds_rate)

    def _spread_schedule_amounts(self, aos_value: float, gst_rate: float = 5, tds_rate: float = 1):
        """Distribute AOS across schedule rows and compute row GST, TDS, Net."""
        for d in self.get("payment_schedule", []):
            d.amount = flt(aos_value * flt(d.percentage) / 100.0, 2)
            d.gst_amount = flt(d.amount * gst_rate / 100.0, 2)
            d.tds_amount = flt(d.amount * tds_rate / 100.0, 2)
            d.net_payable = flt(d.amount + d.gst_amount - d.tds_amount, 2)

    def _compute_before_registration(self):
        """Compute Before Registration charges (Maintenance, Move-in, etc.)"""
        s = frappe.get_single("Realapp Settings")
        area = flt(self.salable_area)

        maint_rate = flt(s.maintenance_rate_per_sft)
        maint_gst_rate = flt(s.maintenance_gst_rate or 18)
        corpus_rate = flt(s.corpus_fund_rate_per_sft)
        move_in_base = flt(s.move_in_charges)
        move_in_gst_rate = flt(s.move_in_gst_rate or 18)
        rcd = flt(s.refundable_caution_deposit)
        regn = flt(s.default_registration_charges)

        # Maintenance
        maintenance_charges = flt(maint_rate * area, 2)
        maintenance_gst = flt(maintenance_charges * maint_gst_rate / 100.0, 2)
        maintenance_amount = flt(maintenance_charges + maintenance_gst, 2)

        # Corpus fund
        corpus_fund = flt(corpus_rate * area, 2)

        # Move-in
        move_in_gst = flt(move_in_base * move_in_gst_rate / 100.0, 2)
        move_in_amount = flt(move_in_base + move_in_gst, 2)

        # Total before registration
        total = flt(maintenance_amount + corpus_fund + rcd + move_in_amount + regn, 2)

        self.maintenance_charges = maintenance_charges
        self.maintenance_gst = maintenance_gst
        # optional if you want to surface maintenance_amount field on doctype
        self.maintenance_amount = maintenance_amount
        self.corpus_fund = corpus_fund
        self.refundable_caution_deposit = rcd
        self.move_in_charges = move_in_base
        self.move_in_gst = move_in_gst
        self.move_in_amount = move_in_amount
        self.registration_charges = regn
        self.before_registration_total = total

    def _compute_grand_total(self):
        """Compute the final grand total payable amount."""
        self.grand_total_payable = flt(self.aos_value_gst or 0) + flt(self.before_registration_total or 0)

# ---------------- Whitelisted helpers ----------------

@frappe.whitelist()
def get_payment_scheme_rows(template: str, block: str = None):
    """
    Fetch Payment Scheme rows from Payment Scheme Template and
    merge in Tower Milestone dates (from Block → Tower Milestone) by scheme_code.
    """
    if not template:
        return []

    doc = frappe.get_doc("Payment Scheme Template", template)

    # scheme_code → milestone_date from Block
    milestone_dates = {}
    if block:
        blk = frappe.get_doc("Block", block)
        for t in blk.get("tower_milestones") or []:
            if t.scheme_code:
                milestone_dates[t.scheme_code] = t.milestone_date

    out = []
    for d in doc.get("payment_scheme_details") or []:
        out.append({
            "scheme_code": d.scheme_code,
            "milestone": d.milestone,
            "milestone_item": d.milestone_item,
            "particulars": d.particulars,
            "percentage": d.percentage,
            "milestone_date": milestone_dates.get(d.scheme_code),
        })
    return out


@frappe.whitelist()
def compute_header_values(base_price_per_sft: float, salable_area: float, value_excluding_bp: float):
    """Stateless server calc for header (AOS/GST/TDS/Net/Eff)."""
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
        effective_rate_per_sft=flt(net / area, 2),
    )

@frappe.whitelist()
def compute_before_registration(salable_area: float):
    """Stateless compute of 'Before Registration' charges (for client refresh)."""
    s = frappe.get_single("Realapp Settings")
    area = flt(salable_area)

    maint_rate = flt(s.maintenance_rate_per_sft)
    maint_gst_rate = flt(s.maintenance_gst_rate or 18)
    corpus_rate = flt(s.corpus_fund_rate_per_sft)
    move_in_base = flt(s.move_in_charges)
    move_in_gst_rate = flt(s.move_in_gst_rate or 18)
    rcd = flt(s.refundable_caution_deposit)
    regn = flt(s.default_registration_charges)

    # Maintenance
    maintenance_charges = flt(maint_rate * area, 2)
    maintenance_gst = flt(maintenance_charges * maint_gst_rate / 100.0, 2)
    maintenance_amount = flt(maintenance_charges + maintenance_gst, 2)

    # Corpus fund
    corpus_fund = flt(corpus_rate * area, 2)

    # Move-in
    move_in_gst = flt(move_in_base * move_in_gst_rate / 100.0, 2)
    move_in_amount = flt(move_in_base + move_in_gst, 2)

    # Total before registration
    total = flt(maintenance_amount + corpus_fund + rcd + move_in_amount + regn, 2)

    return frappe._dict(
        maintenance_charges=maintenance_charges,
        maintenance_gst=maintenance_gst,
        maintenance_amount=maintenance_amount,
        corpus_fund=corpus_fund,
        refundable_caution_deposit=rcd,
        move_in_charges=move_in_base,
        move_in_gst=move_in_gst,
        move_in_amount=move_in_amount,
        registration_charges=regn,
        before_registration_total=total,
    )

# ---------------- Booking Order map (Create button) ----------------

@frappe.whitelist()
def make_booking_order(source_name, target_doc=None):
    """Create Booking Order from Cost Sheet and auto-link back."""

    def postprocess(source, target):
        # Link back both ways
        target.cost_sheet = source.name

        # party info
        target.party_type = source.party_type
        target.party = source.party

        # unit snapshot
        target.unit = source.unit
        target.project = source.project
        target.block = source.block
        target.floor_number = source.floor_number
        target.salable_area = source.salable_area
        target.basic_price_per_sft = source.basic_price_per_sft

        # money
        target.aos_value = source.aos_value
        target.aos_gst = source.aos_gst
        target.aos_value_gst = source.aos_value_gst
        target.net_payable = source.net_payable
        target.grand_total_payable = source.grand_total_payable

        # scheme
        target.payment_scheme_template = source.payment_scheme_template

        # clear child table first to avoid duplicates
        target.set("payment_schedule", [])

        # copy schedule rows manually (so we control fields like milestone_item)
        for d in source.get("payment_schedule") or []:
            target.append("payment_schedule", {
                "scheme_code": d.scheme_code,
                "milestone": d.milestone,
                "milestone_item": getattr(d, "milestone_item", None),
                "particulars": d.particulars,
                "percentage": d.percentage,
                "milestone_date": d.milestone_date,
                "amount": d.amount,
                "gst_amount": d.gst_amount,
                "tds_amount": d.tds_amount,
                "net_payable": d.net_payable,
            })

        # update Cost Sheet with Booking Order link
        frappe.db.set_value("Cost Sheet", source.name, "booking_order", target.name)

    return get_mapped_doc(
        "Cost Sheet",
        source_name,
        {
            "Cost Sheet": {
                "doctype": "Booking Order",
                "field_map": {"name": "cost_sheet"},
                "field_no_map": ["naming_series"],  # prevent copying Cost Sheet series
            },
            # 🔹 explicitly stop automatic mapping of child table
            "Cost Sheet Payment Schedule": {
                "doctype": "Booking Order Payment Schedule",
                "field_no_map": ["*"]
            }
        },
        target_doc,
        postprocess,
    )