// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Lead Scoring Report", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Lead Scoring Report', {
  refresh(frm) {
    if (!frm.is_new()) {
      frm.add_custom_button(__('Recalculate Scores'), () => {
        frappe.call({
          method: "realapp.realapp.lead_scoring.engine.generate_lead_scoring_report",
          args: { template_name: frm.doc.lead_scoring_template },
          freeze: true,
          freeze_message: __("Recalculating scores..."),
          callback: (r) => {
            if (!r.exc) {
              frappe.msgprint(__('New report generated: ') + r.message);
              frappe.set_route('Form', 'Lead Scoring Report', r.message);
            }
          }
        });
      }).addClass('btn-primary');
    }
  }
});
