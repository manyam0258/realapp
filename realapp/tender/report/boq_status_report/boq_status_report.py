# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, date_diff

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{"label": "Sl No", "fieldname": "sl_no", "fieldtype": "Float", "width": 80},
		{"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
		{"label": "Work Package", "fieldname": "work_package", "fieldtype": "Data", "width": 200},
		{"label": "Planned Submission", "fieldname": "boq_submission_date", "fieldtype": "Date", "width": 150},
		{"label": "Actual Submitted", "fieldname": "boq_submitted_date", "fieldtype": "Date", "width": 150},
		{"label": "Status", "fieldname": "boq_status", "fieldtype": "Data", "width": 120},
		{"label": "Delay (Days)", "fieldname": "delay", "fieldtype": "Int", "width": 100},
		{"label": "Section", "fieldname": "category", "fieldtype": "Data", "width": 120}
	]

def get_data(filters):
	query_filters = {}
	if filters.get("project"):
		query_filters["project"] = filters["project"]
	if filters.get("boq_status"):
		query_filters["boq_status"] = filters["boq_status"]

	data = frappe.db.get_all("Tender Calendar", 
		fields=["sl_no", "project", "work_package", "boq_submission_date", "boq_submitted_date", "boq_status", "category"],
		filters=query_filters,
		order_by="sl_no asc"
	)

	for d in data:
		if d.boq_submission_date and d.boq_submitted_date:
			d.delay = date_diff(d.boq_submitted_date, d.boq_submission_date)
		elif d.boq_submission_date and not d.boq_submitted_date:
			today = getdate()
			if today > d.boq_submission_date:
				d.delay = date_diff(today, d.boq_submission_date)
			else:
				d.delay = 0
		else:
			d.delay = 0

	return data
