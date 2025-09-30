// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Block", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Block', {
    // When a Payment Scheme Template is added in available_payment_schemes
    refresh(frm) {
        frm.set_intro("Configure which Payment Scheme Templates are valid for this Block. Tower Milestone dates are shared across all templates.");
    }
});

frappe.ui.form.on('Block Payment Scheme', {
    payment_scheme_template: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (!row.payment_scheme_template) return;

        frappe.db.get_doc('Payment Scheme Template', row.payment_scheme_template).then(doc => {
            let tower_milestones = (frm.doc.tower_milestones || []);

            (doc.payment_scheme_details || [])
                .filter(d => (d.particulars || '').toLowerCase() === 'tower specific')
                .forEach(d => {
                    // Check if milestone already exists in tower_milestones
                    if (!tower_milestones.some(m => m.scheme_code === d.scheme_code)) {
                        let child = frm.add_child('tower_milestones');
                        child.scheme_code = d.scheme_code;
                        child.milestone = d.milestone;
                        // milestone_date left empty for user to enter
                    }
                });

            frm.refresh_field('tower_milestones');
        });
    }
});

