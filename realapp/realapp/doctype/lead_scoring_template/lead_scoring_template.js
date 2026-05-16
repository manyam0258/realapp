// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Lead Scoring Template", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Lead Scoring Template', {
  refresh(frm) {
    // Populate parameters (available on Draft and Submitted if needed)
    if (!frm.is_new()) {
      frm.add_custom_button(__('Populate Parameters'), () => {
        frappe.call({
          method: "realapp.realapp.doctype.lead_scoring_template.lead_scoring_template.populate_parameters",
          args: { template_name: frm.doc.name },
          freeze: true,
          freeze_message: __("Populating parameters..."),
          callback: function (r) {
            if (!r.exc) {
              frm.reload_doc();
              frappe.msgprint(__('Parameters populated.'));
            }
          }
        });
      }).addClass('btn-secondary');

      // Generate report button when submitted
      if (frm.doc.docstatus === 1) {
        frm.add_custom_button(__('Generate Report'), () => {
          frappe.call({
            method: "realapp.realapp.doctype.lead_scoring_engine.engine.generate_lead_scoring_report",
            args: { template_name: frm.doc.name },
            freeze: true,
            freeze_message: __("Queueing lead scoring job..."),
            callback: (r) => {
              if (!r.exc) {
                frappe.msgprint({
                  title: __('Job Queued'),
                  indicator: 'blue',
                  message: __(r.message)
                });
              }
            }
          });
        }).addClass('btn-primary');
      }
    }

    // Listen for realtime events
    frappe.realtime.on('lead_scoring_complete', (data) => {
      if (data.template === frm.doc.name) {
        frappe.show_alert({
          message: __('Lead Scoring Complete: {0}', [data.result]),
          indicator: 'green'
        }, 10);
      }
    });

    frappe.realtime.on('lead_scoring_failed', (data) => {
      if (data.template === frm.doc.name) {
        frappe.show_alert({
          message: __('Lead Scoring Failed: {0}', [data.error]),
          indicator: 'red'
        }, 10);
      }
    });
  }
});

frappe.ui.form.on('Lead Scoring Template Detail', {
  parameter(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.parameter) return;
    frappe.db.get_doc('Lead Scoring Parameter', row.parameter).then(param => {
      // Copy master values to child row (but preserve user weight if set)
      frappe.model.set_value(cdt, cdn, 'field_reference', param.field_reference || '');
      frappe.model.set_value(cdt, cdn, 'scoring_logic_type', param.scoring_logic_type || '');
      frappe.model.set_value(cdt, cdn, 'criteria', param.criteria || '');
      frappe.model.set_value(cdt, cdn, 'max_score', param.max_score || 0);
      frappe.model.set_value(cdt, cdn, 'default_weightage', param.default_weightage || 0);
      frappe.model.set_value(cdt, cdn, 'expression', param.example_expression || '');
      // only set weightage if empty or zero
      if (!row.weightage) {
        frappe.model.set_value(cdt, cdn, 'weightage', param.default_weightage || 0);
      }
      frm.refresh_field('details');
    });
  }
});
