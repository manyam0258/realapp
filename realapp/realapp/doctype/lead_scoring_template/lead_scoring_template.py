# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeadScoringTemplate(Document):
    def validate(self):
        """Ensure total weightage = 100 and update status."""
        total_weight = sum([d.weightage for d in self.details if d.active])
        self.total_weight = total_weight

        if total_weight == 100:
            self.validation_status = "✅ Valid"
        else:
            self.validation_status = f"❌ Invalid (Total: {total_weight})"
            frappe.throw(f"Total weightage must be exactly 100%. Current total: {total_weight}%")

    def on_submit(self):
        """Change status to Active on submit."""
        self.status = "Active"

    def on_cancel(self):
        """Change status back to Inactive on cancel."""
        self.status = "Inactive"

    def on_amend(self):
        """Reset to Draft on amendment."""
        self.status = "Draft"
