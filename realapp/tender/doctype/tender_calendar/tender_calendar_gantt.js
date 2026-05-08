// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.views.gantt["Tender Calendar"] = {
	field_map: {
		start: "boq_submission_date",
		end: "target_date",
		id: "name",
		title: "gantt_title",
		allDay: "all_day",
		progress: "no_of_days", // Just using a field to represent some number
	},
	style_field: "order_status"
};
