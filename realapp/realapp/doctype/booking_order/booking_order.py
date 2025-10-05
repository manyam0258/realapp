# Copyright (c) 2025, surendhranath and contributors
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
