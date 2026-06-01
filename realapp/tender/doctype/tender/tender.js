// Copyright (c) 2026, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tender", {

    order_type(frm) {
        if (frm.doc.order_type === "Service") {
            frm.set_value("indigenous_import", "NA");
        }
    },

    no_of_days_planned(frm) {
        if (frm.doc.no_of_days_planned) {

            let target_date = frappe.datetime.add_days(
                frappe.datetime.get_today(),
                cint(frm.doc.no_of_days_planned)
            );

            frm.set_value("target_date", target_date);
        }
    }

});