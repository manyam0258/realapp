# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeadScoringParameter(Document):
    def validate(self):
        # Validation rules
        if not self.parameter_name:
            frappe.throw("Parameter Name is required.")
        if not self.dimension:
            frappe.throw("Dimension is mandatory.")
        if self.default_weightage and (self.default_weightage < 0 or self.default_weightage > 100):
            frappe.throw("Default weightage must be between 0 and 100.")
        if self.max_score and self.max_score < 0:
            frappe.throw("Maximum score cannot be negative.")
