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
		{"label": "Target Date", "fieldname": "target_date", "fieldtype": "Date", "width": 120},
		{"label": "Order Status", "fieldname": "order_status", "fieldtype": "Data", "width": 120},
		{"label": "Contract Value (Lakhs)", "fieldname": "contract_value_lakhs", "fieldtype": "Currency", "width": 150},
		{"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 120},
		{"label": "Order Type", "fieldname": "order_type", "fieldtype": "Data", "width": 120}
	]

def get_data(filters):
	query_filters = {}
	if filters.get("project"):
		query_filters["project"] = filters["project"]
	if filters.get("order_status"):
		query_filters["order_status"] = filters["order_status"]

	data = frappe.db.get_all("Tender Calendar", 
		fields=["project", "work_package", "target_date", "order_status", "contract_value_lakhs", "category", "order_type"],
		filters=query_filters,
		order_by="target_date asc"
	)
	return data
