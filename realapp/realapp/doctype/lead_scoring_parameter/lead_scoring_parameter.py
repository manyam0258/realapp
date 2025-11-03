# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeadScoringParameter(Document):
    def validate(self):
        if not self.parameter_name:
            frappe.throw("Parameter Name is required.")
        if not self.dimension:
            frappe.throw("Dimension is mandatory.")
        if self.default_weightage is None:
            frappe.throw("Default weightage is required.")
        if not (0 <= float(self.default_weightage) <= 100):
            frappe.throw("Default weightage must be between 0 and 100.")
        if self.max_score is None or float(self.max_score) < 0:
            frappe.throw("Maximum score must be a non-negative number.")

