# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class LeadScoringTemplate(Document):
    def validate(self):
        # Update total_weight but do not block saving; block on submit.
        total_weight = sum([d.weightage for d in self.details if d.active])
        self.total_weight = total_weight
        if total_weight == 100:
            self.validation_status = "✅ Valid"
        else:
            self.validation_status = f"❌ Invalid (Total: {total_weight})"

    def on_submit(self):
        # enforce sum == 100 on submit
        total_weight = sum([d.weightage for d in self.details if d.active])
        self.total_weight = total_weight
        if round(total_weight, 2) != 100.0:
            frappe.throw(f"Total weightage of active parameters must be 100. Current total: {total_weight}")
        self.status = "Active"

    def on_cancel(self):
        self.status = "Inactive"

    def on_amend(self):
        self.status = "Draft"

@frappe.whitelist()
def populate_parameters(template_name):
    """
    Add all active Lead Scoring Parameters to the template if not present.
    Keeps user overrides (weightage, active) for existing rows.
    """
    template = frappe.get_doc("Lead Scoring Template", template_name)
    params = frappe.get_all("Lead Scoring Parameter", filters={"active": 1}, fields=["name", "field_reference", "scoring_logic_type", "criteria", "default_weightage", "max_score", "dimension", "example_expression"])
    existing = {d.parameter for d in template.details}
    for p in params:
        if p["name"] in existing:
            continue
        template.append("details", {
            "parameter": p["name"],
            "dimension": p.get("dimension"),
            "field_reference": p.get("field_reference"),
            "scoring_logic_type": p.get("scoring_logic_type"),
            "criteria": p.get("criteria"),
            "max_score": p.get("max_score") or 0,
            "default_weightage": p.get("default_weightage") or 0,
            "weightage": p.get("default_weightage") or 0,
            "expression": p.get("example_expression") or "",
            "active": 1
        })
    template.save(ignore_permissions=True)
    return True
