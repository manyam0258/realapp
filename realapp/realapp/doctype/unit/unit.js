// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on('Unit', {
    refresh: function(frm) {
        frm.set_intro('Dynamic fields are auto-calculated from Realapp Settings unless overridden here.');

        // 🔹 Auto-fetch Floor Rise Rate, GST, and TDS from settings
        frappe.db.get_single_value("Realapp Settings", "floor_rise_rate").then(rate => {
            if (rate) frm.set_value("floor_rise_rate", rate);
        });
        frappe.db.get_single_value("Realapp Settings", "gst_rate").then(val => {
            if (val) frm.set_value("gst_rate", val);
        });
        frappe.db.get_single_value("Realapp Settings", "tds_rate").then(val => {
            if (val) frm.set_value("tds_rate", val);
        });
    },

    // Triggers
    basic_price_per_sft: function(frm) { frm.trigger("recalculate"); },
    area_in_sft: function(frm) { frm.trigger("recalculate"); },
    amenities_charges_per_sft: function(frm) { frm.trigger("recalculate"); },
    infra_charges_per_sft: function(frm) { frm.trigger("recalculate"); },
    facing_premium_charges: function(frm) { frm.trigger("recalculate"); },
    corner_premium_charges: function(frm) { frm.trigger("recalculate"); },
    car_parking_amount: function(frm) { frm.trigger("recalculate"); },
    documentation_charges: function(frm) { frm.trigger("recalculate"); },
    floor: function(frm) { frm.trigger("recalculate"); },
    is_floor_rise_applicable: function(frm) { frm.trigger("recalculate"); },

    // Main recalculation logic
    recalculate: function(frm) {
        let area = frm.doc.area_in_sft || 0;
        let base = (frm.doc.basic_price_per_sft || 0) * area;
        let infra_amt = (frm.doc.infra_charges_per_sft || 0) * area;
        let amenities_amt = (frm.doc.amenities_charges_per_sft || 0) * area;

        frm.set_value("infra_charges_amt", infra_amt);
        frm.set_value("amenities_charges_amt", amenities_amt);

        // 🔹 Floor Rise Calculation
        if (frm.doc.is_floor_rise_applicable && frm.doc.floor) {
            frappe.db.get_value("Floor", frm.doc.floor, "floor_number").then(r => {
                let floor_number = r.message.floor_number || 0;
                let rate = frm.doc.floor_rise_rate || 20;
                let floor_rise = 0;
                let effective_rate = 0;

                if (floor_number >= 5) {
                    effective_rate = (floor_number - 4) * rate;
                    floor_rise = effective_rate * area;
                }

                frm.set_value("effective_floor_rise_rate", effective_rate);
                frm.set_value("floor_rise_charges", floor_rise);

                frm.events.calculate_totals(frm, base, infra_amt, amenities_amt, floor_rise);
            });
        } else {
            frm.set_value("effective_floor_rise_rate", 0);
            frm.set_value("floor_rise_charges", 0);
            frm.events.calculate_totals(frm, base, infra_amt, amenities_amt, 0);
        }
    },

    // Helper: calculates totals, GST, TDS, Net Payable
    calculate_totals: function(frm, base, infra_amt, amenities_amt, floor_rise) {
        let full_value = base
            + infra_amt
            + amenities_amt
            + floor_rise
            + (frm.doc.facing_premium_charges || 0)
            + (frm.doc.corner_premium_charges || 0)
            + (frm.doc.car_parking_amount || 0)
            + (frm.doc.documentation_charges || 0);

        frm.set_value("full_unit_value", full_value);

        let value_ex_bp = infra_amt + amenities_amt
            + floor_rise
            + (frm.doc.facing_premium_charges || 0)
            + (frm.doc.corner_premium_charges || 0)
            + (frm.doc.car_parking_amount || 0)
            + (frm.doc.documentation_charges || 0);
        frm.set_value("value_excluding_bp", value_ex_bp);

        // AOS + GST
        let gst_rate = frm.doc.gst_rate || 5;
        let aos_with_gst = full_value * (1 + gst_rate / 100);
        frm.set_value("aos_value", full_value);
        frm.set_value("aos_value_gst_5", aos_with_gst);

        // TDS
        let tds_rate = frm.doc.tds_rate || 1;
        let tds_val = full_value * (tds_rate / 100);
        frm.set_value("tds_1", tds_val);

        // Net payable
        frm.set_value("net_payable", aos_with_gst - tds_val);
    }
});
