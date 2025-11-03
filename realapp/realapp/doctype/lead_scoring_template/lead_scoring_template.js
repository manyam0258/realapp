// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Lead Scoring Template", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Lead Scoring Template', {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.docstatus === 1) {
      frm.add_custom_button(__('Generate Report'), () => {
        frappe.call({
          method: "realapp.realapp.doctype.lead_scoring_engine.engine.generate_lead_scoring_report",
          args: { template_name: frm.doc.name },
          freeze: true,
          freeze_message: __("Generating lead scoring reports..."),
          callback: (r) => {
            if (!r.exc) {
              frappe.msgprint(__(r.message));
              frappe.set_route('List', 'Lead Scoring Report');
            }
          }
        });
      }).addClass('btn-primary');
    }
  }
});

