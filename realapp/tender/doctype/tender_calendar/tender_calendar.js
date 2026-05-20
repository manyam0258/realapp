// Copyright (c) 2026, Antigravity and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender Calendar", {
	refresh(frm) {
		frm.trigger("set_indicators");
		
		// Cache initial BOQ submission date for Suggestion Mode cascading comparison
		frm.old_boq_submission_date = frm.doc.boq_submission_date;

		// Set document badge to order_status
		let status = frm.doc.order_status || "Pending";
		let color = "orange";
		if (status === "Issued") color = "green";
		if (status === "Cancelled") color = "red";
		frm.page.set_indicator(status, color);

		// Tower Wise Generation Button
		if (frm.doc.project_type === "Tower Wise" && !frm.doc.towers_generated && !frm.doc.__islocal) {
			frm.add_custom_button(__("Generate Tower Tenders"), () => {
				frappe.call({
					method: "realapp.tender.doctype.tender_calendar.tender_calendar.get_remaining_blocks",
					args: { docname: frm.doc.name },
					callback: function(r) {
						let blocks = r.message || [];
						if (blocks.length === 0) {
							frappe.msgprint(__("No remaining blocks to generate tenders for."));
							return;
						}

						// Build checkbox HTML
						let html = '<div style="max-height: 250px; overflow-y: auto; padding: 10px 15px;">';
						blocks.forEach(block => {
							let label = block.tower_name ? `${block.tower_name} (${block.name})` : block.name;
							html += `
								<div class="checkbox" style="margin-bottom: 8px;">
									<label style="cursor: pointer; display: flex; align-items: center;">
										<input type="checkbox" class="block-select" value="${block.name}" checked style="margin-right: 8px;">
										<span>${label}</span>
									</label>
								</div>
							`;
						});
						html += '</div>';

						let dialog = new frappe.ui.Dialog({
							title: __("Select Blocks/Towers"),
							fields: [
								{
									fieldtype: "HTML",
									fieldname: "blocks_list_html"
								}
							],
							primary_action_label: __("Generate"),
							primary_action() {
								let selected_blocks = [];
								dialog.$wrapper.find('.block-select:checked').each(function() {
									selected_blocks.push($(this).val());
								});

								if (selected_blocks.length === 0) {
									frappe.msgprint(__("Please select at least one block."));
									return;
								}

								dialog.hide();

								frappe.call({
									method: "realapp.tender.doctype.tender_calendar.tender_calendar.generate_selected_tower_tenders",
									args: {
										docname: frm.doc.name,
										selected_blocks: selected_blocks
									},
									freeze: true,
									freeze_message: __("Generating Tenders..."),
									callback: function(res) {
										if (!res.exc) {
											frappe.show_alert({
												message: __("Tower Tenders Generated Successfully"),
												indicator: "green"
											});
											frm.reload_doc();
										}
									}
								});
							}
						});

						dialog.show();
						dialog.fields_dict.blocks_list_html.set_value(html);
					}
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
		let old_date = frm.old_boq_submission_date;
		if (!old_date) {
			frm.old_boq_submission_date = frm.doc.boq_submission_date;
			return;
		}

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
					frm.old_boq_submission_date = frm.doc.boq_submission_date;
				},
				() => {
					frm.old_boq_submission_date = frm.doc.boq_submission_date;
				}
			);
		} else {
			frm.old_boq_submission_date = frm.doc.boq_submission_date;
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
