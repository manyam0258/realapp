// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Lead Scoring Template", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Lead Scoring Template', {
  refresh(frm) {
    if (!frm.is_new() && frm.doc.docstatus === 1) { // Only after Submit
      frm.add_custom_button(__('Generate Report'), () => {
        frappe.call({
          method: "realapp.realapp.doctype.lead_scoring_engine.engine.generate_lead_scoring_report",
          args: { template_name: frm.doc.name },
          freeze: true,
          freeze_message: __("Generating Lead Scoring Report..."),
          callback: (r) => {
            if (!r.exc) {
              frappe.msgprint(__('Report Generated: ') + r.message);
              frappe.set_route('Form', 'Lead Scoring Report', r.message);
            }
          }
        });
      }).addClass('btn-primary');
    }
  }
});
