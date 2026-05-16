// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender Calendar", {
	refresh(frm) {
		frm.trigger("set_indicators");
		
		// Set document badge to order_status
		let color = "orange";
		if (frm.doc.order_status === "Issued") color = "green";
		if (frm.doc.order_status === "Cancelled") color = "red";
		frm.page.set_indicator(frm.doc.order_status, color);

		// Tower Wise Generation Button
		if (frm.doc.project_type === "Tower Wise" && !frm.doc.towers_generated && !frm.doc.__islocal) {
			frm.add_custom_button(__("Generate Tower Tenders"), () => {
				frappe.confirm(__("This will create individual Tender Calendar records for each Block/Tower in this Project. Do you want to proceed?"), () => {
					frappe.call({
						method: "realapp.tender.doctype.tender_calendar.tender_calendar.generate_tower_tenders",
						args: { docname: frm.doc.name },
						freeze: true,
						freeze_message: __("Generating Towers..."),
						callback: function(r) {
							if (!r.exc) {
								frappe.show_alert({ message: __("Tower Tenders Generated Successfully"), indicator: "green" });
								frm.reload_doc();
							}
						}
					});
				});
			}, __("Actions"));
		}
	},

	boq_submission_date(frm) {
		if (frm.doc.cascading_mode === "Suggestion" && frm.doc.boq_submission_date) {
			frm.trigger("propose_cascade");
		}
	},

	set_indicators(frm) {
		if (frm.doc.impact_level === "Critical" || frm.doc.impact_level === "High") {
			frm.set_df_property("impact_level", "description", "<b style='color:red'>Critical Delay Impact</b>");
		}
	},

	propose_cascade(frm) {
		// Logic to calculate shift based on old value
		// For simplicity in JS, we compare against original doc if available
		let old_date = frm.doc.__onsave && frm.doc.__onsave.boq_submission_date;
		if (!old_date) return;

		let delta = frappe.datetime.get_diff(frm.doc.boq_submission_date, old_date);
		if (delta > 0) {
			frappe.confirm(
				`BOQ Submission delayed by ${delta} days. Shift all downstream dates?`,
				() => {
					// Apply shifts
					frm.set_value("tender_issue_date", frappe.datetime.add_days(frm.doc.tender_issue_date, delta));
					frm.set_value("approval_date", frappe.datetime.add_days(frm.doc.approval_date, delta + 2));
					frm.set_value("contract_date", frappe.datetime.add_days(frm.doc.contract_date, delta + 5));
					frm.set_value("mobilization_date", frappe.datetime.add_days(frm.doc.mobilization_date, delta + 10));
					frm.set_value("target_date", frappe.datetime.add_days(frm.doc.target_date, delta + 10));
					
					frappe.show_alert({
						message: __("Downstream dates shifted successfully"),
						indicator: "green"
					});
				}
			);
		}
	},

	validate(frm) {
		// Chronological sequence validation
		let dates = [
			{ label: "BOQ Submission", date: frm.doc.boq_submission_date },
			{ label: "Tender Issue", date: frm.doc.tender_issue_date },
			{ label: "Approval", date: frm.doc.approval_date },
			{ label: "Contract", date: frm.doc.contract_date },
			{ label: "Mobilization", date: frm.doc.mobilization_date }
		];

		for (let i = 0; i < dates.length - 1; i++) {
			if (dates[i].date && dates[i+1].date) {
				if (frappe.datetime.get_diff(dates[i+1].date, dates[i].date) < 0) {
					frappe.msgprint({
						title: __("Sequence Warning"),
						message: __("{0} should be before {1}", [dates[i].label, dates[i+1].label]),
						indicator: "orange"
					});
				}
			}
		}
	}
});
