import frappe
from frappe.model.meta import get_meta

def execute():
    """Patch to add Unit Base Amount field and reload Unit doctype."""
    doctype = "Unit"
    fieldname = "unit_base_amount"

    frappe.reload_doc("realapp", "doctype", "unit")

    meta = get_meta(doctype)
    existing_fields = [df.fieldname for df in meta.fields]
    if fieldname not in existing_fields:
        frappe.db.add_column(doctype, fieldname, "decimal(18,6)")
        frappe.logger().info(f"✅ Added missing column '{fieldname}' in {doctype} table.")
    else:
        frappe.logger().info(f"ℹ️ Column '{fieldname}' already exists in {doctype} table.")

    frappe.db.commit()
    frappe.logger().info(f"🔄 Reloaded {doctype} doctype successfully with new field.")
