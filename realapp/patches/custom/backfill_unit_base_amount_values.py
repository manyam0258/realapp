import frappe
from frappe.utils import flt

def execute():
    """
    Backfill Unit Base Amount for all existing Unit records.
    Formula: basic_price_per_sft * salable_area
    """

    doctype = "Unit"
    if not frappe.db.has_column(doctype, "unit_base_amount"):
        frappe.logger().warning(f"⚠️ Column 'unit_base_amount' not found in {doctype}. Skipping backfill.")
        return

    units = frappe.get_all(doctype, fields=["name", "basic_price_per_sft", "salable_area"])
    if not units:
        frappe.logger().info("ℹ️ No Unit records found for backfill.")
        return

    updated = 0
    for u in units:
        base = flt(u.basic_price_per_sft or 0)
        area = flt(u.salable_area or 0)
        value = flt(base * area, 2)

        frappe.db.set_value(doctype, u.name, "unit_base_amount", value)
        updated += 1

    frappe.db.commit()
    frappe.logger().info(f"✅ Backfilled {updated} Unit records with Unit Base Amount values.")
