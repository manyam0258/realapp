// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.listview_settings['Tender Calendar'] = {
	get_indicator: function(doc) {
		if (doc.order_status === "Issued") {
			return [__("Issued"), "green", "order_status,=,Issued"];
		} else if (doc.order_status === "Cancelled") {
			return [__("Cancelled"), "red", "order_status,=,Cancelled"];
		} else {
			return [__("Pending"), "orange", "order_status,=,Pending"];
		}
	}
};
