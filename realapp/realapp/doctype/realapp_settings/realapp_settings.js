// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Realapp Settings", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Realapp Settings', {
    refresh: function(frm) {
        frm.set_intro('These settings act as default values for Unit pricing and charges. Unit overrides take priority.');
    }
});

