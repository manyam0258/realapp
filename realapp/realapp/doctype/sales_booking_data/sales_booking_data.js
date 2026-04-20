// Copyright (c) 2026, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Booking Data", {
	refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Consolidated Docs'), function() {
                frappe.call({
                    method: "realapp.realapp.doctype.sales_booking_data.sales_booking_data.consolidate_documents",
                    args: {
                        docname: frm.doc.name
                    },
                    freeze: true,
                    freeze_message: __("Processing and consolidating documents..."),
                    callback: function(r) {
                        if (r.message) {
                            let file_url = r.message;
                            
                            let d = new frappe.ui.Dialog({
                                title: __("Consolidated Documents Preview"),
                                size: "extra-large",
                                fields: [
                                    {
                                        fieldname: "pdf_preview",
                                        fieldtype: "HTML",
                                        options: `<iframe src="${file_url}" style="width: 100%; height: 75vh; border: none;"></iframe>`
                                    }
                                ],
                                primary_action_label: __("Open in New Tab"),
                                primary_action: function() {
                                    window.open(file_url, '_blank');
                                }
                            });
                            d.show();
                        }
                    }
                });
            }, __("Actions"));
        }
	},
});
