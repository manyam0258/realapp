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
		{"label": "Min Vendors Req", "fieldname": "min_vendors_required", "fieldtype": "Int", "width": 120},
		{"label": "Current Vendor Count", "fieldname": "vendor_count", "fieldtype": "Int", "width": 150},
		{"label": "Coverage Status", "fieldname": "coverage", "fieldtype": "Data", "width": 120},
		{"label": "RFQ Status", "fieldname": "order_status", "fieldtype": "Data", "width": 120},
		{"label": "Indig / Import", "fieldname": "indigenous_import", "fieldtype": "Data", "width": 120}
	]

def get_data(filters):
	query_filters = {}
	if filters.get("project"):
		query_filters["project"] = filters["project"]
	
	data = frappe.db.get_all("Tender Calendar", 
		fields=["project", "work_package", "min_vendors_required", "vendor_count", "order_status", "indigenous_import"],
		filters=query_filters,
		order_by="project, work_package"
	)

	for d in data:
		if d.vendor_count >= (d.min_vendors_required or 0):
			d.coverage = "Full"
		elif d.vendor_count > 0:
			d.coverage = "Partial"
		else:
			d.coverage = "None"
			
	return data
