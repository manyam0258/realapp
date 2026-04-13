# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": "Work Package", "fieldname": "work_package", "fieldtype": "Data", "width": 200},
		{"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 120},
		{"label": "BOQ Status", "fieldname": "boq_status", "fieldtype": "Data", "width": 120},
		{"label": "BOQ Planned", "fieldname": "boq_submission_date", "fieldtype": "Date", "width": 120},
		{"label": "BOQ Actual", "fieldname": "boq_submitted_date", "fieldtype": "Date", "width": 120},
		{"label": "Tender Issue", "fieldname": "tender_issue_date", "fieldtype": "Date", "width": 120},
		{"label": "Approval", "fieldname": "approval_date", "fieldtype": "Date", "width": 120},
		{"label": "Contract", "fieldname": "contract_date", "fieldtype": "Date", "width": 120},
		{"label": "Mobilization", "fieldname": "mobilization_date", "fieldtype": "Date", "width": 120},
		{"label": "Target Date", "fieldname": "target_date", "fieldtype": "Date", "width": 120},
		{"label": "Order Status", "fieldname": "order_status", "fieldtype": "Data", "width": 120},
		{"label": "Impact", "fieldname": "impact_level", "fieldtype": "Data", "width": 100}
	]

def get_data(filters):
	query_filters = {}
	if filters.get("project"):
		query_filters["project"] = filters["project"]
	if filters.get("category"):
		query_filters["category"] = filters["category"]
	if filters.get("impact_level"):
		query_filters["impact_level"] = filters["impact_level"]

	data = frappe.db.get_all("Tender Calendar", 
		fields=[
			"project", "work_package", "category", "boq_status", 
			"boq_submission_date", "boq_submitted_date", "tender_issue_date", 
			"approval_date", "contract_date", "mobilization_date", 
			"target_date", "order_status", "impact_level"
		],
		filters=query_filters,
		order_by="project, target_date asc"
	)
	return data
