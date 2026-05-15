// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.views.calendar["Tender Calendar"] = {
	field_map: {
		start: "target_date",
		end: "target_date",
		id: "name",
		allDay: "all_day",
		title: "work_package",
		project_status: "status",
	},
	style_field: "status",
	colors: {
		"Pending": "orange",
		"Issued": "green",
		"Cancelled": "red"
	},
	get_events_method: "realapp.tender.doctype.tender_calendar.tender_calendar.get_calendar_events"
};
