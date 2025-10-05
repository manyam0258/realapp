// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking Order', {
  setup(frm) {
    frm.set_query("cost_sheet", () => {
      return {
        filters: {
          unit: frm.doc.unit || ""  // only cost sheets of the selected unit
        }
      };
    });
  },

  unit(frm) {
    if (frm.doc.unit && frm.doc.cost_sheet) {
      // Reload cost sheet snapshot
      pull_cost_sheet_snapshot(frm);
    }
  },

  cost_sheet(frm) {
    if (frm.doc.cost_sheet) {
      pull_cost_sheet_snapshot(frm);
    }
  },

  advance_paid(frm) {
    compute_balance(frm);
  }
});

// ----------------- Helpers -----------------

function pull_cost_sheet_snapshot(frm) {
  frappe.call({
    method: "frappe.client.get",
    args: {
      doctype: "Cost Sheet",
      name: frm.doc.cost_sheet
    },
    callback(r) {
      if (!r.message) return;
      const cs = r.message;

      frm.set_value({
        project: cs.project,
        block: cs.block,
        floor_number: cs.floor_number,
        salable_area: cs.salable_area,
        basic_price_per_sft: cs.basic_price_per_sft,
        aos_value: cs.aos_value,
        aos_gst: cs.aos_gst,
        aos_value_gst: cs.aos_value_gst,
        net_payable: cs.net_payable,
        grand_total_payable: cs.grand_total_payable,
        payment_scheme_template: cs.payment_scheme_template
      });

      // Pull child table rows
      frm.clear_table("payment_schedule");
      (cs.payment_schedule || []).forEach(row => {
        let child = frm.add_child("payment_schedule");
        frappe.model.set_value(child.doctype, child.name, "scheme_code", row.scheme_code);
        frappe.model.set_value(child.doctype, child.name, "milestone", row.milestone);
        frappe.model.set_value(child.doctype, child.name, "particulars", row.particulars);
        frappe.model.set_value(child.doctype, child.name, "percentage", row.percentage);
        frappe.model.set_value(child.doctype, child.name, "milestone_date", row.milestone_date);
        frappe.model.set_value(child.doctype, child.name, "amount", row.amount);
        frappe.model.set_value(child.doctype, child.name, "gst_amount", row.gst_amount);
        frappe.model.set_value(child.doctype, child.name, "tds_amount", row.tds_amount);
        frappe.model.set_value(child.doctype, child.name, "net_payable", row.net_payable);
      });
      frm.refresh_field("payment_schedule");

      compute_balance(frm);
    }
  });
}

function compute_balance(frm) {
  const adv = flt(frm.doc.advance_paid);
  const total = flt(frm.doc.grand_total_payable);
  frm.set_value("balance_payable", total - adv);
}

function flt(v) { const n = parseFloat(v); return isNaN(n) ? 0 : n; }