// Copyright (c) 2026, surendhranath and contributors
// For license information, please see license.txt

let is_updating_schedule = false;

frappe.ui.form.on("Procurement Contract", {
    setup(frm) {
        frm.set_query("party_type", function () {
            return {
                filters: {
                    name: ["in", ["Supplier", "Customer"]]
                }
            };
        });
    },

    refresh(frm) {
        // Show create options when document is submitted
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            const fulfillment = (frm.doc.fulfillment_type || frm.doc.fulfillmant_type || "").trim();

            if (fulfillment === "Purchase Order" || fulfillment === "Both") {
                frm.add_custom_button(__("Purchase Order"), () => {
                    frappe.model.open_mapped_doc({
                        method: "realapp.realapp.doctype.procurement_contract.procurement_contract.make_purchase_order",
                        frm: frm
                    });
                }, __("Create"));
            }

            if (fulfillment === "Purchase Receipt" || fulfillment === "Both") {
                frm.add_custom_button(__("Purchase Receipt"), () => {
                    frappe.model.open_mapped_doc({
                        method: "realapp.realapp.doctype.procurement_contract.procurement_contract.make_purchase_receipt",
                        frm: frm
                    });
                }, __("Create"));
            }
        }
    },

    // Trigger schedule generation on frequency or date changes
    contract_frequency(frm) {
        frm.trigger("generate_schedule");
    },
    frequency(frm) {
        frm.trigger("generate_schedule");
    },
    start_date(frm) {
        frm.trigger("generate_schedule");
    },
    end_date(frm) {
        frm.trigger("generate_schedule");
    },

    generate_schedule(frm) {
        const freq = frm.doc.contract_frequency || frm.doc.frequency;
        if (!frm.doc.start_date || !frm.doc.end_date || !freq || freq === "One-time") {
            return;
        }

        let start = moment(frm.doc.start_date);
        let end = moment(frm.doc.end_date);

        if (end.isBefore(start)) {
            return;
        }

        // Clear existing rows to rebuild fresh milestone periods
        frm.clear_table("schedules");

        let cur = start.clone();

        while (cur.isBefore(end) || cur.isSame(end, "day")) {
            let period_start = cur.clone();
            let period_end;
            let label = "";

            if (freq === "Monthly") {
                period_end = cur.clone().endOf("month");
                if (period_end.isAfter(end)) period_end = end.clone();
                label = period_start.format("MMM YYYY");
                cur.add(1, "month").startOf("month");
            } else if (freq === "Quarterly") {
                period_end = cur.clone().add(3, "months").subtract(1, "day");
                if (period_end.isAfter(end)) period_end = end.clone();
                label = `Q${period_start.quarter()} ${period_start.format("YYYY")}`;
                cur.add(3, "months");
            } else if (freq === "Half-Yearly") {
                period_end = cur.clone().add(6, "months").subtract(1, "day");
                if (period_end.isAfter(end)) period_end = end.clone();
                label = `H${period_start.month() < 6 ? 1 : 2} ${period_start.format("YYYY")}`;
                cur.add(6, "months");
            } else if (freq === "Yearly") {
                period_end = cur.clone().add(1, "year").subtract(1, "day");
                if (period_end.isAfter(end)) period_end = end.clone();
                label = `Year ${period_start.format("YYYY")}`;
                cur.add(1, "year");
            }

            let row = frm.add_child("schedules");
            row.period_label = label;
            row.from_date = period_start.format("YYYY-MM-DD");
            row.to_date = period_end.format("YYYY-MM-DD");
            row.qty = 1; // Default to 1 so math works
            row.rate = 0;
            row.amount = 0;
            row.status = "Pending";
        }

        frm.refresh_field("schedules");

        // Automatically distribute total contract value if already present
        if (flt(frm.doc.total_contract_value) > 0) {
            frm.trigger("total_contract_value");
        }
    },

    // When the user changes Total Contract Value -> Distribute across rows
    total_contract_value(frm) {
        if (is_updating_schedule) return;
        if (!frm.doc.schedules || frm.doc.schedules.length === 0) return;

        is_updating_schedule = true;
        let total_val = flt(frm.doc.total_contract_value);
        let row_count = frm.doc.schedules.length;
        let per_row_amount = flt(total_val / row_count, 2);

        frm.doc.schedules.forEach((row) => {
            let qty = flt(row.qty) > 0 ? flt(row.qty) : 1;
            row.qty = qty;
            row.amount = per_row_amount;
            row.rate = flt(per_row_amount / qty, 2);
        });

        frm.refresh_field("schedules");
        is_updating_schedule = false;
    }
});

// Handling events on the Child Table: Procurement Contract Schedule Item
frappe.ui.form.on("Procurement Contract Schedule Item", {
    // Auto-fetch item details when item_code is picked
    item_code(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code) {
            frappe.db.get_value("Item", row.item_code, ["item_name", "stock_uom", "description"])
                .then(r => {
                    if (r && r.message) {
                        frappe.model.set_value(cdt, cdn, "item_name", r.message.item_name);
                    }
                });
        }
    },

    qty(frm, cdt, cdn) {
        recalculate_child_row(frm, cdt, cdn);
    },

    rate(frm, cdt, cdn) {
        recalculate_child_row(frm, cdt, cdn);
    },

    schedules_remove(frm) {
        sync_total_contract_value(frm);
    }
});

function recalculate_child_row(frm, cdt, cdn) {
    if (is_updating_schedule) return;
    let row = locals[cdt][cdn];
    row.amount = flt(row.qty) * flt(row.rate);
    frm.refresh_field("schedules");
    sync_total_contract_value(frm);
}

function sync_total_contract_value(frm) {
    if (is_updating_schedule) return;
    is_updating_schedule = true;
    let total = 0;
    (frm.doc.schedules || []).forEach(row => {
        total += flt(row.amount);
    });
    frm.set_value("total_contract_value", total);
    is_updating_schedule = false;
}