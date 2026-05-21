// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.listview_settings['Tender Calendar'] = {
	get_indicator: function(doc) {
		let state = doc.workflow_state || "Tender Creation";
		let color = "orange";
		if (state === "Completed") {
			color = "green";
		} else if (state === "Tender Creation") {
			color = "gray";
		} else {
			color = "blue";
		}
		return [__(state), color, "workflow_state,=," + state];
	}
};
