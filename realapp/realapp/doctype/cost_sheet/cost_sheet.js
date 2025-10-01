frappe.ui.form.on('Cost Sheet', {
    refresh: async function(frm) {
        frm.set_intro("Quick Entry → Party + Unit. System auto-fills Project/Block/Floor, pulls rates, and calculates everything.");

        // Lock/Unlock Basic Price for Standard vs Customized
        frm.set_df_property("basic_price_per_sft", "read_only", frm.doc.cost_sheet_type === "Standard");

        // Ensure tax/rate fields are loaded for client-side preview if empty
        await ensure_settings_defaults(frm);

        // Custom button: Generate Payment Schedule (filtered by Block if possible)
        if (!frm.is_new()) {
            frm.add_custom_button(__('Generate Payment Schedule'), async function() {
                let allowed = [];
                if (frm.doc.block) {
                    try {
                        const block = await frappe.db.get_doc('Block', frm.doc.block);
                        const rows = (block.available_payment_schemes || []).filter(r => r.payment_scheme_template);
                        allowed = rows.map(r => r.payment_scheme_template);
                    } catch(e) { /* ignore */ }
                }

                // Build dialog
                const d = new frappe.ui.Dialog({
                    title: __('Select Payment Scheme'),
                    fields: [
                        {
                            label: 'Payment Scheme Template',
                            fieldname: 'template_name',
                            fieldtype: allowed.length ? 'Select' : 'Link',
                            options: allowed.length ? [''].concat(allowed) : 'Payment Scheme Template',
                            reqd: 1
                        }
                    ],
                    primary_action_label: __('Generate'),
                    primary_action: async (values) => {
                        d.hide();
                        await frappe.call({
                            method: "realapp.realapp.doctype.cost_sheet.cost_sheet.CostSheet.generate_schedule_from_template",
                            doc: frm.doc,
                            args: { template_name: values.template_name }
                        });
                        frm.reload_doc();
                        frappe.msgprint(__('Payment Schedule generated from template.'));
                    }
                });
                d.show();
            });
        }
    },

    cost_sheet_type: function(frm) {
        frm.set_df_property("basic_price_per_sft", "read_only", frm.doc.cost_sheet_type === "Standard");
        frm.trigger('recalculate');
    },

    // FIX: Dynamic Link → refresh Party options when Party Type is changed
    party_type: function(frm) {
        if (frm.doc.party_type) {
            frm.set_df_property("party", "options", frm.doc.party_type);
            frm.refresh_field("party");
        }
    },

    unit: async function(frm) {
        if (!frm.doc.unit) return;

        const unit = await frappe.db.get_doc("Unit", frm.doc.unit);

        // Auto-link Floor → Block → Project, and capture floor_no
        frm.set_value("floor", unit.floor || null);

        if (unit.floor) {
            const floor = await frappe.db.get_doc("Floor", unit.floor);
            frm.set_value("floor_no", floor.floor_no || 0);
            frm.set_value("block", floor.block || null);

            if (floor.block) {
                const block = await frappe.db.get_doc("Block", floor.block);
                frm.set_value("project", block.project || null);
            }
        }

        // Pricing inputs from Unit (override Settings)
        frm.set_value("basic_price_per_sft", unit.basic_price_per_sft);
        frm.set_value("amenities_charges_per_sft", unit.amenities_charges_per_sft);
        frm.set_value("infra_charges_per_sft", unit.infra_charges_per_sft);
        frm.set_value("facing_premium_charges", unit.facing_premium_charges);
        frm.set_value("corner_premium_charges", unit.corner_premium_charges);
        frm.set_value("car_parking_amount", unit.car_parking_amount);
        frm.set_value("documentation_charges", unit.documentation_charges);

        // Areas / attributes snapshot
        frm.set_value("builtup_area", unit.area_in_sft);
        frm.set_value("carpet_area", unit.carpet_area);
        frm.set_value("balcony_area", unit.balcony_area);
        frm.set_value("uds", unit.uds);
        frm.set_value("facing", unit.facing);
        frm.set_value("corner_preference", unit.corner_preference);

        // Floor rise rate from Settings (server also applies, but set for preview)
        const settings = await frappe.db.get_single('Realapp Settings');
        frm.set_value('floor_rise_rate', settings.floor_rise_rate || 0);

        frm.trigger('recalculate');
    },

    // Inputs that impact calculations
    basic_price_per_sft: function(frm) { frm.trigger('recalculate'); },
    amenities_charges_per_sft: function(frm) { frm.trigger('recalculate'); },
    infra_charges_per_sft: function(frm) { frm.trigger('recalculate'); },
    builtup_area: function(frm) { frm.trigger('recalculate'); },
    carpet_area: function(frm) { frm.trigger('recalculate'); },
    floor_no: function(frm) { frm.trigger('recalculate'); },
    registration_charges: function(frm) { frm.trigger('recalculate'); },
    maintenance_rate_per_sft: function(frm) { frm.trigger('recalculate'); },
    corpus_fund_rate_per_sft: function(frm) { frm.trigger('recalculate'); },
    refundable_caution_deposit: function(frm) { frm.trigger('recalculate'); },
    move_in_charges: function(frm) { frm.trigger('recalculate'); },

    recalculate: function(frm) {
        // Client-side preview (server will also recheck on save)
        const area = (frm.doc.builtup_area || frm.doc.carpet_area || 0) * 1.0;

        const base = (frm.doc.basic_price_per_sft || 0) * area;

        let floor_rise = 0;
        const floor_no = frm.doc.floor_no || 0;
        const floor_rise_rate = frm.doc.floor_rise_rate || 0;
        if (floor_no >= 5) {
            floor_rise = (floor_no - 4) * floor_rise_rate * area;
        }

        const infra_amt = (frm.doc.infra_charges_per_sft || 0) * area;
        const amenities_amt = (frm.doc.amenities_charges_per_sft || 0) * area;

        const agreement_value =
            base + floor_rise + infra_amt + amenities_amt +
            (frm.doc.facing_premium_charges || 0) +
            (frm.doc.corner_premium_charges || 0) +
            (frm.doc.car_parking_amount || 0) +
            (frm.doc.documentation_charges || 0);

        frm.set_value('base_price_value', base);
        frm.set_value('floor_rise_charges', floor_rise);
        frm.set_value('infra_charges_amt', infra_amt);
        frm.set_value('amenities_charges_amt', amenities_amt);
        frm.set_value('agreement_value', agreement_value);

        // Before Registration: Maintenance / Corpus / Deposits / Regn
        const maintenance_total = (frm.doc.maintenance_rate_per_sft || 0) * area;
        const maintenance_gst_rate = frm.doc.maintenance_gst_rate || 18;
        const maintenance_gst = maintenance_total * maintenance_gst_rate / 100.0;
        const corpus_total = (frm.doc.corpus_fund_rate_per_sft || 0) * area;

        frm.set_value('maintenance_total', maintenance_total);
        frm.set_value('maintenance_gst', maintenance_gst);
        frm.set_value('corpus_fund_total', corpus_total);

        // GST on Agreement Value (summary)
        const gst_rate = frm.doc.gst_rate || 5;
        const tds_rate = frm.doc.tds_rate || 1;
        const gst_total = agreement_value * gst_rate / 100.0;
        frm.set_value('gst_total', gst_total);

        // Explicit totals
        frm.set_value('registration_charges_total', frm.doc.registration_charges || 0);
        frm.set_value('other_deposits_total',
            (frm.doc.refundable_caution_deposit || 0) + (frm.doc.move_in_charges || 0)
        );

        // Grand total
        const grand_total = agreement_value + gst_total +
            (frm.doc.registration_charges || 0) +
            maintenance_total + maintenance_gst +
            corpus_total +
            (frm.doc.refundable_caution_deposit || 0) +
            (frm.doc.move_in_charges || 0);

        frm.set_value('grand_total_payable', grand_total);

        // Recompute child schedule preview
        (frm.doc.payment_schedule || []).forEach(row => {
            row.amount = agreement_value * (row.percentage || 0) / 100.0;
            row.gst_amount = row.amount * gst_rate / 100.0;
            row.tds_amount = row.amount * tds_rate / 100.0;
            row.net_payable = row.amount + row.gst_amount - row.tds_amount;
        });
        frm.refresh_field('payment_schedule');
    }
});

/** Ensure GST/TDS/Maintenance/Floor-rise defaults are loaded into the form
 *  so client-side math shows correct preview even before save. */
async function ensure_settings_defaults(frm) {
    const need =
        !frm.doc.gst_rate || !frm.doc.tds_rate ||
        frm.doc.maintenance_gst_rate == null || frm.doc.floor_rise_rate == null;

    if (!need) return;

    try {
        const settings = await frappe.db.get_single('Realapp Settings');
        if (!frm.doc.gst_rate) frm.set_value('gst_rate', settings.gst_rate || 5);
        if (!frm.doc.tds_rate) frm.set_value('tds_rate', settings.tds_rate || 1);
        if (frm.doc.maintenance_gst_rate == null)
            frm.set_value('maintenance_gst_rate', settings.maintenance_gst_rate || 18);
        if (frm.doc.floor_rise_rate == null)
            frm.set_value('floor_rise_rate', settings.floor_rise_rate || 0);
    } catch (e) { /* ignore */ }
}
