import frappe
from frappe.utils import flt

def execute():
    """
    Backfill Facing Premium Amount & Corner Premium Amount for all existing Unit records.
    Formula:
        facing_premium_amount = facing_premium_charges * salable_area
        corner_premium_amount = corner_premium_charges * salable_area
    """
    doctype = "Unit"
    if not (frappe.db.has_column(doctype, "facing_premium_amount") and frappe.db.has_column(doctype, "corner_premium_amount")):
        frappe.logger().warning("⚠️ Missing required columns in Unit table. Skipping backfill.")
        return

    units = frappe.get_all(doctype, fields=["name", "salable_area", "facing_premium_charges", "corner_premium_charges"])
    if not units:
        frappe.logger().info("ℹ️ No Unit records found for backfill.")
        return

    updated = 0
    for u in units:
        area = flt(u.salable_area or 0)
        facing_rate = flt(u.facing_premium_charges or 0)
        corner_rate = flt(u.corner_premium_charges or 0)

        if area <= 0:
            continue

        facing_amt = flt(facing_rate * area, 2)
        corner_amt = flt(corner_rate * area, 2)

        frappe.db.set_value(doctype, u.name, {
            "facing_premium_amount": facing_amt,
            "corner_premium_amount": corner_amt
        })
        updated += 1

    frappe.db.commit()
    frappe.logger().info(f"✅ Backfilled {updated} Unit records with Facing & Corner Premium Amount values.")
