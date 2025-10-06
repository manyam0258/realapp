// Copyright (c) 2025, surendhranath
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

  refresh(frm) {
    // Add Create Sales Invoice button only after submission
    if (!frm.is_new() && frm.doc.docstatus === 1) {
      frm.add_custom_button(__('Sales Invoice'), () => {
        open_milestone_dialog(frm);
      }, __('Create'));
    }
  },

  unit(frm) {
    if (frm.doc.unit && frm.doc.cost_sheet) {
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
        frappe.model.set_value(child.doctype, child.name, "milestone_item", row.milestone_item);
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

// ----------------- Milestone → Invoice Dialog -----------------
function open_milestone_dialog(frm) {
  let d = new frappe.ui.Dialog({
    title: 'Select Milestones for Sales Invoice',
    fields: [
      {
        fieldtype: 'Table',
        fieldname: 'milestones',
        label: 'Milestones',
        cannot_add_rows: true,
        in_place_edit: false,
        data: (frm.doc.payment_schedule || []).map(r => {
          return {
            name: r.name,                // 🔹 add row identifier
            scheme_code: r.scheme_code,
            milestone: r.milestone,
            milestone_item: r.milestone_item,
            amount: r.amount,
            milestone_date: r.milestone_date
          };
        }),
        get_data: function() { return this.data; },
        fields: [
          { fieldtype: 'Check', fieldname: 'selected', label: '✓', in_list_view: 1, width: '5%' },
          { fieldtype: 'Data', fieldname: 'milestone', label: 'Milestone', in_list_view: 1, read_only: 1, width: '25%' },
          { fieldtype: 'Link', fieldname: 'milestone_item', label: 'Item', options: 'Item', in_list_view: 1, read_only: 1, width: '20%' },
          { fieldtype: 'Currency', fieldname: 'amount', label: 'Amount', in_list_view: 1, read_only: 1, width: '15%' },
          { fieldtype: 'Date', fieldname: 'milestone_date', label: 'Due Date', in_list_view: 1, read_only: 1, width: '15%' }
        ]
      }
    ],
    primary_action_label: 'Create Sales Invoice',
    primary_action(values) {
      let selected_rows = (values.milestones || [])
        .filter(r => r.selected)
        .map(r => r.name);   // now works

      if (!selected_rows.length) {
        frappe.msgprint(__('Please select at least one milestone.'));
        return;
      }

      frappe.call({
        method: "realapp.realapp.doctype.booking_order.booking_order.make_sales_invoice",
        args: {
          source_name: frm.doc.name,
          selected_rows: JSON.stringify(selected_rows)
        },
        callback(r) {
          if (r.message) {
            frappe.model.sync(r.message);
            frappe.set_route('Form', r.message.doctype, r.message.name);
          }
        }
      });

      d.hide();
    }
  });

  d.show();
}
