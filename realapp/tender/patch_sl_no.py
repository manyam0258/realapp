import frappe

def patch_data():
    with open('/tmp/patch_log.txt', 'w') as log:
        try:
            log.write("Starting patch...\n")
            all_items = frappe.get_all(
                "Tender Calendar", 
                order_by="creation ASC", 
                fields=["name", "work_package", "block", "is_template"]
            )
            
            master_items = [i for i in all_items if not i.get('block')]
            
            log.write(f"Found {len(master_items)} master items.\n")

            seq = 1.0
            for item in master_items:
                frappe.db.set_value("Tender Calendar", item.name, "sl_no", seq)
                log.write(f"Set {item.name} to {seq}\n")
                
                # Find its generated towers (if any)
                towers = [t for t in all_items if t.get('block') and t.get('work_package', '').startswith(item.get('work_package', '') + " - ")]
                
                if towers:
                    sub_seq = 0.1
                    for t in towers:
                        new_val = round(seq + sub_seq, 1)
                        frappe.db.set_value("Tender Calendar", t.name, "sl_no", new_val)
                        log.write(f"  Set {t.name} to {new_val}\n")
                        sub_seq += 0.1
                        
                seq += 1.0

            frappe.db.commit()
            log.write("Patch successful!\n")
        except Exception as e:
            frappe.db.rollback()
            log.write(f"Error: {str(e)}\n")
