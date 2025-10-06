# Copyright (c) 2025, surendhranath
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc


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


# ---------------- Create Sales Invoice from Booking Order ----------------

@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None, selected_rows=None):
    """
    Create Sales Invoice from Booking Order.
    User can select specific milestones (payment_schedule rows).
    """

    def postprocess(source, target):
        # Always link Booking Order
        target.booking_order = source.name

        # --- Handle Party / Customer ---
        if source.party_type == "Customer":
            target.customer = source.party
        else:
            # Create or fetch Customer from Lead/Opportunity
            customer = ensure_customer_from_party(source.party, source.party_type)
            target.customer = customer.name

        # Mirror Realapp-specific fields
        target.realapp_unit = source.unit
        target.realapp_project = source.project
        target.realapp_block = source.block
        target.realapp_floor_number = source.floor_number

        # Copy selected milestones → SI items
        if selected_rows:
            rows = frappe.parse_json(selected_rows)
            for d in source.get("payment_schedule"):
                if d.name in rows:
                    target.append("items", {
                        "item_code": d.milestone_item or None,
                        "description": d.milestone or d.particulars,
                        "milestone_code": d.scheme_code,
                        "qty": 1,
                        "rate": d.amount,
                        "amount": d.amount,
                        "due_date": d.milestone_date,
                        "project": source.project
                    })

    return get_mapped_doc(
        "Booking Order",
        source_name,
        {
            "Booking Order": {
                "doctype": "Sales Invoice",
                "field_no_map": ["naming_series"],
            }
        },
        target_doc,
        postprocess
    )


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
