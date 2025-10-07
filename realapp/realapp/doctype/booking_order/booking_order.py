# Copyright (c) 2025, surendhranath
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class BookingOrder(Document):
    def validate(self):
        self._pull_cost_sheet_snapshot()
        self._compute_balance()

    def on_submit(self):
        # Validate Unit Availability
        unit = frappe.get_doc("Unit", self.unit)
        if unit.status != "Available":
            frappe.throw(f"Unit {self.unit} is not available (current status: {unit.status}).")

        # Mark as Booked
        unit.status = "Booked"
        unit.save(ignore_permissions=True)

    def on_cancel(self):
        # Revert Unit back to Available if booking cancelled
        if self.unit:
            unit = frappe.get_doc("Unit", self.unit)
            if unit.status == "Booked":
                unit.status = "Available"
                unit.save(ignore_permissions=True)

    # ----------------- Helpers -----------------

    def _pull_cost_sheet_snapshot(self):
        """Mirror key values from Cost Sheet & Unit"""
        if not self.cost_sheet:
            frappe.throw("Please select a Cost Sheet.")

        cs = frappe.get_doc("Cost Sheet", self.cost_sheet)

        # Unit & pricing snapshot
        self.project = cs.project
        self.block = cs.block
        self.floor_number = cs.floor_number
        self.salable_area = cs.salable_area
        self.basic_price_per_sft = cs.basic_price_per_sft
        self.aos_value = cs.aos_value
        self.aos_gst = cs.aos_gst
        self.aos_value_gst = cs.aos_value_gst
        self.net_payable = cs.net_payable
        self.grand_total_payable = cs.grand_total_payable
        self.payment_scheme_template = cs.payment_scheme_template

        # Clear & copy payment schedule
        self.set("payment_schedule", [])
        for row in cs.get("payment_schedule") or []:
            self.append("payment_schedule", {
                "scheme_code": row.scheme_code,
                "milestone": row.milestone,
                "milestone_item": row.milestone_item,
                "particulars": row.particulars,
                "percentage": row.percentage,
                "milestone_date": row.milestone_date,
                "amount": row.amount,
                "gst_amount": row.gst_amount,
                "tds_amount": row.tds_amount,
                "net_payable": row.net_payable
            })

    def _compute_balance(self):
        """Compute balance payable = grand_total - advance"""
        adv = flt(self.advance_paid or 0.0)
        total = flt(self.grand_total_payable or 0.0)
        self.balance_payable = flt(total - adv, 2)


# ---------------- Utilities ----------------

def get_item_defaults(item_code: str, company: str) -> dict:
    """Fetch defaults (uom, accounts, cost center) for given Item + Company."""
    if not item_code:
        return {}

    # Item basics
    item = frappe.db.get_value(
        "Item",
        item_code,
        ["item_name", "stock_uom"],
        as_dict=True,
    ) or {}

    # Company-specific defaults from Item Default child
    defaults = frappe.db.get_value(
        "Item Default",
        {"parent": item_code, "company": company},
        ["income_account", "expense_account", "buying_cost_center", "selling_cost_center"],
        as_dict=True,
    ) or {}

    # Company fallback
    company_defaults = frappe.db.get_value(
        "Company",
        company,
        ["default_income_account", "cost_center"],
        as_dict=True,
    ) or {}

    return {
        "item_name": item.get("item_name"),
        "uom": item.get("stock_uom"),  # stock uom always available
        "income_account": defaults.get("income_account") or company_defaults.get("default_income_account"),
        "cost_center": defaults.get("selling_cost_center") or company_defaults.get("cost_center"),
    }


# ---------------- Create Sales Invoice ----------------

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, selected_rows=None):
    """
    Create Sales Invoice(s) from Booking Order milestones.
    - If user selects 1 milestone → open a single invoice form.
    - If user selects multiple milestones → create multiple draft invoices silently.
    """

    bo = frappe.get_doc("Booking Order", source_name)
    rows = frappe.parse_json(selected_rows) if selected_rows else []

    if not rows:
        frappe.throw("No milestones selected.")

    chosen = [r for r in bo.payment_schedule if r.name in rows]

    if len(chosen) == 1:
        # single invoice → open form
        return _build_single_sales_invoice(bo, chosen[0])
    else:
        # multiple invoices → insert in background
        si_list = []
        for row in chosen:
            si = _build_single_sales_invoice(bo, row, save=True)
            si_list.append(si.name)

        frappe.msgprint(f"{len(si_list)} draft Sales Invoices created: {', '.join(si_list)}")
        return None


def _build_single_sales_invoice(bo, row, save=False):
    """Helper: build a Sales Invoice for a specific milestone row."""
    company = frappe.db.get_default("company") or frappe.get_all("Company", limit=1)[0].name

    defaults = get_item_defaults(row.milestone_item, company) if row.milestone_item else {}

    si = frappe.new_doc("Sales Invoice")
    si.company = company
    si.booking_order = bo.name

    # Customer mapping
    if bo.party_type == "Customer":
        si.customer = bo.party
    else:
        customer = ensure_customer_from_party(bo.party, bo.party_type)
        si.customer = customer.name

    # Realapp context
    si.realapp_unit = bo.unit
    si.realapp_project = bo.project
    si.realapp_block = bo.block
    si.realapp_floor_number = bo.floor_number

    # Set due_date at parent level if milestone_date exists
    if row.milestone_date:
        si.due_date = row.milestone_date

    # Add item
    si.append("items", {
        "item_code": row.milestone_item,
        "item_name": defaults.get("item_name"),
        "description": row.milestone or row.particulars,
        "qty": 1,
        "uom": defaults.get("uom"),
        "rate": row.amount,
        "amount": row.amount,
        "income_account": defaults.get("income_account"),
        "cost_center": defaults.get("cost_center"),
        "project": bo.project,
    })

    if save:
        si.insert(ignore_permissions=True)
        return si

    return si


def ensure_customer_from_party(party_name, party_type):
    """
    Convert Lead/Opportunity into Customer if needed.
    Returns the Customer doc.
    """
    if party_type == "Lead":
        lead = frappe.get_doc("Lead", party_name)
        if getattr(lead, "converted_by", None):
            return frappe.get_doc("Customer", lead.converted_by)

        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": lead.lead_name,
            "lead_name": lead.name,
            "customer_type": "Individual",
            "customer_group": "All Customer Groups",
            "territory": "All Territories"
        }).insert(ignore_permissions=True)

        lead.converted_by = customer.name
        lead.save(ignore_permissions=True)
        return customer

    elif party_type == "Opportunity":
        opp = frappe.get_doc("Opportunity", party_name)
        if opp.customer:
            return frappe.get_doc("Customer", opp.customer)

        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": opp.party_name or f"Customer {party_name}",
            "customer_type": "Individual",
            "customer_group": "All Customer Groups",
            "territory": "All Territories"
        }).insert(ignore_permissions=True)

        opp.customer = customer.name
        opp.save(ignore_permissions=True)
        return customer

    else:
        return frappe.get_doc("Customer", party_name)
