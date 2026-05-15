// Custom Lead Form Script
// Adds "Generate Score" button to score individual leads

frappe.ui.form.on('Lead', {
    refresh(frm) {
        if (!frm.is_new()) {
            // Add "Generate Score" button
            frm.add_custom_button(__('Generate Score'), () => {
                // Create dialog to select Lead Scoring Template
                let d = new frappe.ui.Dialog({
                    title: __('Select Lead Scoring Template'),
                    fields: [
                        {
                            label: __('Lead Scoring Template'),
                            fieldname: 'template',
                            fieldtype: 'Link',
                            options: 'Lead Scoring Template',
                            reqd: 1,
                            get_query: function () {
                                return {
                                    filters: {
                                        'docstatus': 1  // Only submitted templates
                                    }
                                };
                            }
                        }
                    ],
                    primary_action_label: __('Generate Score'),
                    primary_action(values) {
                        d.hide();

                        frappe.call({
                            method: "realapp.realapp.doctype.lead_scoring_engine.engine.score_specific_leads",
                            args: {
                                template_name: values.template,
                                lead_names: frm.doc.name
                            },
                            freeze: true,
                            freeze_message: __("Calculating lead score..."),
                            callback: (r) => {
                                if (!r.exc && r.message && r.message.length > 0) {
                                    const result = r.message[0];

                                    // Show score result
                                    frappe.msgprint({
                                        title: __('Lead Score Generated'),
                                        indicator: result.category === 'Hot' ? 'green' : result.category === 'Warm' ? 'orange' : 'blue',
                                        message: `
                      <div style="font-size: 14px;">
                        <p><strong>${__('Template')}:</strong> ${values.template}</p>
                        <p><strong>${__('Score')}:</strong> <span style="font-size: 18px; font-weight: bold; color: ${result.category === 'Hot' ? 'green' : result.category === 'Warm' ? 'orange' : 'blue'};">${result.score}</span> / 100</p>
                        <p><strong>${__('Category')}:</strong> ${result.category}</p>
                        <p><a href="/app/lead-scoring-report/${result.report_name}" target="_blank">${__('View Detailed Report')}</a></p>
                      </div>
                    `
                                    });

                                    // Show alert
                                    frappe.show_alert({
                                        message: __('Score: {0} - {1}', [result.score, result.category]),
                                        indicator: result.category === 'Hot' ? 'green' : result.category === 'Warm' ? 'orange' : 'blue'
                                    }, 5);
                                }
                            }
                        });
                    }
                });

                d.show();
            }, __('Actions'));
        }
    }
});
