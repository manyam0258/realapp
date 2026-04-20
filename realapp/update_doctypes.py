import frappe

def execute():
    doc = frappe.get_doc('DocType', 'SBD Attachment')
    doc.custom = 0
    doc.flags.ignore_permissions = True
    doc.save()
    print("SBD Attachment set to custom=0 and saved successfully.")
    
    # Also ensure there are no permission errors if it's considered standard but tracking is missed.
    frappe.db.commit()
