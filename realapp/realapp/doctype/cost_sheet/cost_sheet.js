// Copyright (c) 2025
// For license information, please see license.txt

frappe.ui.form.on('Cost Sheet', {
  setup(frm) {
    // Recalculate amounts in child when % changes
    frm.set_query('payment_scheme_template', () => ({}));
  },

  refresh(frm) {
    toggle_basic_price_editability(frm);
  },

  cost_sheet_type(frm) {
    toggle_basic_price_editability(frm);
    if (frm.doc.unit) {
      pull_unit_numbers(frm).then(() => {
        recalc_header_from_base(frm);   // ensure AOS etc. reflect type
        recalc_schedule_amounts(frm);
        recalc_before_registration_and_grand_total(frm);
      });
    }
  },

  unit(frm) {
    if (!frm.doc.unit) return;
    pull_unit_numbers(frm).then(() => {
      // For Standard type, lock base to Unit.basic_price_per_sft
      if (frm.doc.cost_sheet_type === 'Standard') {
        frm.set_value('basic_price_per_sft', frm.__unit_ctx.base_rate || 0);
      }
      recalc_header_from_base(frm);
      recalc_schedule_amounts(frm);
      recalc_before_registration_and_grand_total(frm);
    });
  },

  basic_price_per_sft(frm) {
    // Only meaningful for Negotiated type
    recalc_header_from_base(frm);
    recalc_schedule_amounts(frm);
    recalc_before_registration_and_grand_total(frm);
  },

  payment_scheme_template(frm) {
    if (frm.doc.payment_scheme_template) {
      frappe.call({
        method: "realapp.realapp.doctype.cost_sheet.cost_sheet.get_payment_scheme_rows",
        args: { template: frm.doc.payment_scheme_template },
        callback(r) {
          if (r.message) {
            frm.clear_table("cost_sheet_payment_schedule");  // 👈 Cost Sheet child table
            r.message.forEach(row => {
              let child = frm.add_child("cost_sheet_payment_schedule");
              frappe.model.set_value(child.doctype, child.name, "scheme_code", row.scheme_code);
              frappe.model.set_value(child.doctype, child.name, "milestone", row.milestone);
              frappe.model.set_value(child.doctype, child.name, "particulars", row.particulars);
              frappe.model.set_value(child.doctype, child.name, "percentage", row.percentage);
            });
            frm.refresh_field("cost_sheet_payment_schedule");
          }
        }
      });
    }
  },

  // When user edits % in rows, recompute row amount + totals
  payment_schedule_percentage(frm, cdt, cdn) {
    recalc_schedule_amounts(frm);
  },

  // Safety: if user edits template rows manually, always recompute
  payment_schedule_add(frm) { recalc_schedule_amounts(frm); },
  payment_schedule_remove(frm) { recalc_schedule_amounts(frm); },
});

// ---------- helpers ----------

function toggle_basic_price_editability(frm) {
  const negotiated = frm.doc.cost_sheet_type === 'Negotiated';
  frm.set_df_property('basic_price_per_sft', 'read_only', !negotiated);
  frm.refresh_field('basic_price_per_sft');
}

/**
 * Pull current Unit values into the Cost Sheet.
 * Saves a small context object on the form so Negotiated math is easy.
 */
function pull_unit_numbers(frm) {
  return frappe.db.get_doc('Unit', frm.doc.unit).then(u => {
    frm.__unit_ctx = {
      area: flt(u.salable_area),
      base_rate: flt(u.basic_price_per_sft),
      ex_bp: flt(u.value_excluding_bp),             // (rise + facing + corner)*area + car park
      aos_value: flt(u.aos_value),
      aos_gst: flt(u.aos_gst),
      aos_value_gst: flt(u.aos_value_gst),
      tds_amount: flt(u.tds_amount),
      net_payable: flt(u.net_payable),
      eff_rate: flt(u.effective_rate_per_sft),
      project: u.project || '',
      block: u.block || '',
      floor_number: cint(u.floor_number)
    };

    frm.set_value({
      project: frm.__unit_ctx.project,
      block: frm.__unit_ctx.block,
      floor_number: frm.__unit_ctx.floor_number,
      salable_area: frm.__unit_ctx.area
    });

    // For Standard type mirror Unit numbers; for Negotiated we'll recompute below
    if (frm.doc.cost_sheet_type === 'Standard') {
      frm.set_value({
        basic_price_per_sft: frm.__unit_ctx.base_rate,
        full_unit_value: flt(u.full_unit_value),
        value_excluding_bp: frm.__unit_ctx.ex_bp,
        aos_value: frm.__unit_ctx.aos_value,
        aos_gst: frm.__unit_ctx.aos_gst,
        aos_value_gst: frm.__unit_ctx.aos_value_gst,
        tds_amount: frm.__unit_ctx.tds_amount,
        net_payable: frm.__unit_ctx.net_payable,
        effective_rate_per_sft: frm.__unit_ctx.eff_rate
      });
    } else {
      // Negotiated – keep ex_bp from Unit, recompute header numbers from current base
      frm.set_value('value_excluding_bp', frm.__unit_ctx.ex_bp);
    }
  });
}

function recalc_header_from_base(frm) {
  const area  = flt(frm.doc.salable_area);
  const ex_bp = flt(frm.doc.value_excluding_bp);         // from Unit
  const base  = flt(frm.doc.basic_price_per_sft);

  if (area <= 0) {
    frm.set_value({
      aos_value: 0, aos_gst: 0, aos_value_gst: 0,
      tds_amount: 0, net_payable: 0, effective_rate_per_sft: 0
    });
    return;
  }

  // Ask server for GST/TDS (single source of truth) and computed header
  frappe.call({
    method: 'realapp.realapp.doctype.cost_sheet.cost_sheet.compute_header_values',
    args: { base_price_per_sft: base, salable_area: area, value_excluding_bp: ex_bp }
  }).then(r => {
    const v = (r && r.message) || {};
    frm.set_value({
      full_unit_value: v.full_unit_value,              // recomputed like Unit (info)
      aos_value: v.aos_value,
      aos_gst: v.aos_gst,
      aos_value_gst: v.aos_value_gst,
      tds_amount: v.tds_amount,
      net_payable: v.net_payable,
      effective_rate_per_sft: v.effective_rate_per_sft,
    });
  });
}

function recalc_schedule_amounts(frm) {
  const aos = flt(frm.doc.aos_value);
  (frm.doc.payment_schedule || []).forEach(r => {
    r.amount = flt(aos * flt(r.percentage) / 100.0);
  });
  frm.refresh_field('payment_schedule');
}

function recalc_before_registration_and_grand_total(frm) {
  // Compute (read-only) before-registration items from settings on server to avoid drift
  frappe.call({
    method: 'realapp.realapp.doctype.cost_sheet.cost_sheet.compute_before_registration',
    args: { salable_area: flt(frm.doc.salable_area) }
  }).then(r => {
    const b = (r && r.message) || {};
    frm.set_value({
      maintenance_charges: b.maintenance_charges,
      maintenance_gst: b.maintenance_gst,
      corpus_fund: b.corpus_fund,
      refundable_caution_deposit: b.refundable_caution_deposit,
      move_in_charges: b.move_in_charges,
      registration_charges: b.registration_charges,
      before_registration_total: b.before_registration_total
    });

    const grand_total = flt(frm.doc.aos_value_gst) + flt(b.before_registration_total);
    frm.set_value('grand_total_payable', grand_total);
  });
}

// tiny numeric helpers
function flt(v) { const n = parseFloat(v); return isNaN(n) ? 0 : n; }
function cint(v) { const n = parseInt(v, 10); return isNaN(n) ? 0 : n; }
