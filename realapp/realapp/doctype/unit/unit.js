// For license information, please see license.txt

frappe.ui.form.on('Unit', {
  refresh(frm) {
    frm.set_intro('Select Floor Name → Block, Project, and Floor Number auto-filled. Pricing auto-calculates.');

    // Show Create Cost Sheet button (only if doc is saved and not cancelled)
    if (!frm.is_new() && frm.doc.docstatus < 2) {
      frm.add_custom_button(__('Cost Sheet'), () => {
        create_cost_sheet(frm);
      }, __('Create'));
    }
  },

  // Trigger when Floor Name is selected
  floor_name: function(frm) {
    if (frm.doc.floor_name) {
      frappe.db.get_doc('Floor', frm.doc.floor_name).then(floor => {
        if (floor.block) {
          frm.set_value('block', floor.block);

          frappe.db.get_doc('Block', floor.block).then(block => {
            if (block.project) {
              frm.set_value('project', block.project);
            }
          });
        }
        if (floor.floor_number) {
          frm.set_value('floor_number', floor.floor_number);
        }
      });
    }
  },

  // Recalculation triggers
  salable_area: recalc,
  basic_price_per_sft: recalc,
  floor_rise_rate: recalc,
  facing_premium_charges: recalc,
  corner_premium_charges: recalc,
  car_parking_amount: recalc,
  documentation_charges: recalc, // NEW
  amenities_charges_per_sft: recalc,
  infra_charges_per_sft: recalc,
  gst_rate: recalc,
  tds_rate: recalc
});

// ---------- helpers ----------

function nz(v) {
  const n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

function recalc(frm) {
  const area        = nz(frm.doc.salable_area);
  const base_rate   = nz(frm.doc.basic_price_per_sft);
  const rise_rate   = nz(frm.doc.floor_rise_rate);
  const facing_rate = nz(frm.doc.facing_premium_charges);
  const corner_rate = nz(frm.doc.corner_premium_charges);
  const car_park    = nz(frm.doc.car_parking_amount);
  const doc_charges = nz(frm.doc.documentation_charges); // NEW

  const amen_rate   = nz(frm.doc.amenities_charges_per_sft);
  const infra_rate  = nz(frm.doc.infra_charges_per_sft);

  const gst_rate    = nz(frm.doc.gst_rate || 5);
  const tds_rate    = nz(frm.doc.tds_rate || 1);

  if (area <= 0) {
    frm.set_value({
      amenities_charges_amt: 0,
      infra_charges_amt: 0,
      floor_rise_charges_amt: 0,
      full_unit_value: 0,
      value_excluding_bp: 0,
      aos_value: 0,
      aos_gst: 0,
      aos_value_gst: 0,
      tds_amount: 0,
      net_payable: 0,
      effective_rate_per_sft: 0,
      unit_base_amount: 0
    });
    return;
  }

  const amen_amt  = amen_rate * area;
  const infra_amt = infra_rate * area;
  const floor_rise_amt = rise_rate * area;

  frm.set_value("amenities_charges_amt", amen_amt);
  frm.set_value("infra_charges_amt", infra_amt);
  frm.set_value("floor_rise_charges_amt", floor_rise_amt);

  // NEW
  const unit_base = area * base_rate;
  frm.set_value("unit_base_amount", unit_base);

  const full_value = (area * (base_rate + rise_rate + facing_rate + corner_rate)) + car_park + doc_charges;
  frm.set_value("full_unit_value", full_value);

  const ex_bp = (area * (rise_rate + facing_rate + corner_rate)) + car_park + doc_charges;
  frm.set_value("value_excluding_bp", ex_bp);

  const aos = (base_rate * area) + ex_bp;
  frm.set_value("aos_value", aos);

  const aos_gst = aos * (gst_rate / 100);
  frm.set_value("aos_gst", aos_gst);

  const aos_with_gst = aos + aos_gst;
  frm.set_value("aos_value_gst", aos_with_gst);

  const tds = aos * (tds_rate / 100);
  frm.set_value("tds_amount", tds);

  const net = aos_with_gst - tds;
  frm.set_value("net_payable", net);
  frm.set_value("effective_rate_per_sft", area ? net / area : 0);
}

// ---------- Create Cost Sheet button ----------

function create_cost_sheet(frm) {
  frappe.model.open_mapped_doc({
    method: "realapp.realapp.doctype.unit.unit.make_cost_sheet",
    frm: frm
  });
}
