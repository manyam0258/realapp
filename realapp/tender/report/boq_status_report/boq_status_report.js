// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.query_reports["BOQ Status Report"] = {
	"filters": [
		{
			"fieldname": "project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
			"reqd": 0
		},
		{
			"fieldname": "boq_status",
			"label": __("BOQ Status"),
			"fieldtype": "Select",
			"options": "\nYet to Submit\nSubmitted\nNA",
			"reqd": 0
		}
	]
};
