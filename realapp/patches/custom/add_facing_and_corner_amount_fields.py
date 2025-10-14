import frappe
from frappe.model.meta import get_meta

def execute():
    """Add Facing Premium Amount and Corner Premium Amount fields to Unit table (if missing)."""
    doctype = "Unit"
    fields_to_add = {
        "facing_premium_amount": "decimal(18,6)",
        "corner_premium_amount": "decimal(18,6)"
    }

    frappe.reload_doc("realapp", "doctype", "unit")

    meta = get_meta(doctype)
    existing_fields = [df.fieldname for df in meta.fields]

    for fieldname, datatype in fields_to_add.items():
        if fieldname not in existing_fields:
            frappe.db.add_column(doctype, fieldname, datatype)
            frappe.logger().info(f"✅ Added missing column '{fieldname}' in {doctype} table.")
        else:
            frappe.logger().info(f"ℹ️ Column '{fieldname}' already exists in {doctype} table.")

    frappe.db.commit()
    frappe.logger().info(f"🔄 Reloaded {doctype} doctype successfully with new premium amount fields.")
