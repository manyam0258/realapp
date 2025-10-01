// For license information, please see license.txt

frappe.ui.form.on('Unit', {
  refresh(frm) {
    frm.set_intro('Amenities & Infra amounts are shown for info; Full/AOS follow Excel rules.');
  },

  salable_area: recalc,
  basic_price_per_sft: recalc,
  floor_rise_rate: recalc,
  facing_premium_charges: recalc,
  corner_premium_charges: recalc,
  car_parking_amount: recalc,
  amenities_charges_per_sft: recalc,
  infra_charges_per_sft: recalc,
  gst_rate: recalc,
  tds_rate: recalc
});

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

  const amen_rate   = nz(frm.doc.amenities_charges_per_sft);
  const infra_rate  = nz(frm.doc.infra_charges_per_sft);

  const gst_rate    = nz(frm.doc.gst_rate || 5);
  const tds_rate    = nz(frm.doc.tds_rate || 1);

  if (area <= 0) {
    frm.set_value({
      amenities_charges_amt: 0,
      infra_charges_amt: 0,
      full_unit_value: 0,
      value_excluding_bp: 0,
      aos_value: 0,
      aos_value_gst: 0,
      tds_amount: 0,
      net_payable: 0,
      effective_rate_per_sft: 0
    });
    return;
  }

  // Informational amounts
  const amen_amt  = amen_rate * area;
  const infra_amt = infra_rate * area;
  frm.set_value("amenities_charges_amt", amen_amt);
  frm.set_value("infra_charges_amt", infra_amt);

  // Excel rules:
  const full_value = area * (base_rate + rise_rate + facing_rate + corner_rate) + car_park;
  frm.set_value("full_unit_value", full_value);

  const ex_bp = area * (rise_rate + facing_rate + corner_rate) + car_park;
  frm.set_value("value_excluding_bp", ex_bp);

  const aos = (base_rate * area) + ex_bp;
  frm.set_value("aos_value", aos);

  const aos_with_gst = aos * (1 + gst_rate / 100);
  const tds = aos * (tds_rate / 100);
  frm.set_value("aos_value_gst", aos_with_gst);
  frm.set_value("tds_amount", tds);

  const net = aos_with_gst - tds;
  frm.set_value("net_payable", net);
  frm.set_value("effective_rate_per_sft", area ? net / area : 0);
}
