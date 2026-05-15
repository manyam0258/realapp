# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	
	# Optional: Add charts
	chart = get_chart(data)
	
	return columns, data, None, chart

def get_columns():
	return [
		{"label": "Month", "fieldname": "month", "fieldtype": "Data", "width": 100},
		{"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": "Work Package", "fieldname": "work_package", "fieldtype": "Data", "width": 200},
		{"label": "Category", "fieldname": "category", "fieldtype": "Data", "width": 120},
		{"label": "BOQ Target", "fieldname": "boq_submission_date", "fieldtype": "Date", "width": 120},
		{"label": "Tender Issue", "fieldname": "tender_issue_date", "fieldtype": "Date", "width": 120},
		{"label": "Order Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": "Contract Value", "fieldname": "contract_value_lakhs", "fieldtype": "Currency", "width": 120}
	]

def get_data(filters):
	query_filters = {}
	if filters.get("project"):
		query_filters["project"] = filters["project"]
	if filters.get("target_month"):
		# Custom filtering logic for month if needed
		pass

	data = frappe.db.get_all("Tender Calendar", 
		fields=[
			"DATE_FORMAT(target_date, '%%M %%Y') as month", 
			"project", "work_package", "category", 
			"boq_submission_date", "tender_issue_date", 
			"status", "contract_value_lakhs", "target_date"
		],
		filters=query_filters,
		order_by="target_date asc"
	)
	return data

def get_chart(data):
	if not data:
		return None
		
	# Aggregate by month for chart
	months = {}
	for d in data:
		m = d.month
		months[m] = months.get(m, 0) + 1
		
	labels = list(months.keys())
	values = list(months.values())
	
	return {
		"data": {
			"labels": labels,
			"datasets": [{"name": "Tenders", "values": values}]
		},
		"type": "bar",
		"colors": ["#3498db"]
	}
