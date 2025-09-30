# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaymentSchemeTemplate(Document):
    def validate(self):
        seen = set()
        total_pct = 0.0

        for row in self.payment_scheme_details:
            # Prevent duplicate codes inside same template
            if row.scheme_code in seen:
                frappe.throw(f"Duplicate Code {row.scheme_code} in template {self.scheme_name}")
            seen.add(row.scheme_code)

            total_pct += (row.percentage or 0)

        if total_pct > 100.0:
            frappe.throw(f"Total percentage in {self.scheme_name} exceeds 100%. Found {total_pct}%.")