import frappe

WORK_PACKAGES_ORDER = [
    "Shell and Core Works Tender(including Water proofing)",
    "Reinforcement material",
    "Shortcreting/ Gunneting",
    "Aluminium Shuttering Material-1st Order",
    "Aluminium Shuttering Material-2nd Order",
    "MS Railing Works -Balcony/ODU & Staircase",
    "Putty & Paint",
    "Temporary Door For all flats",
    "Tile Flooring & Dado/ Granite works",
    "Tiles Material Order",
    "Service Order for Tiles work including screed work",
    "UPVC Windows/ Aluminium joinery",
    "Gypsum Boxing/ Cornice",
    "Toilet False Ceiling",
    "Door Frames & Shutters",
    "Doors Hardware",
    "External walls Texture & Painting",
    "External walls Texture & Painting  ",
    "ODU Shaft Louvers",
    "Elevation Features",
    "Lobby Finishes",
    "Expansion Joint Tray",
    "Deep Cleaning & Handing over",
    "STP Works - Electro Mechanical Works",
    "Temporary DB & Electrification works",
    "Temporary Plumbing works",
    "Lifts",
    "Sub Soil & Surface Dainage in Basements",
    "External Drainage & Sewage works",
    "External watersupply & Borewell interconnection",
    "IPHE works including Piping",
    "Diverters & Flush Valve",
    "CP & Sanitary Fittings",
    "Water Meter",
    "Subsoil & Surface drain Pumps including Auto Level Controllers etc.",
    "Pumps for UG Sump, Rain water Sumps including Auto Level Controllers etc.",
    "Earthing & LPS",
    "Internal Electrical works incl Switches/Fixtures",
    "Lights Fixtures",
    "External Electrical works",
    "BMS incl Energy Meters & Gas Meters",
    "Security, CCTV & Access Control",
    "Data & Communication works",
    "External lighting works",
    "Street Light, External  Fixtures",
    "EV Charging point works",
    "Mechanical Ventilation",
    "D.G & Accessories",
    "RMU, HT Panels, MDB's, SMDB's",
    "Transformers",
    "Bus Duct & Cables",
    "Solar power for common area",
    "Solar Fencing",
    "Fire Fighting works incl FA & PA works",
    "Fire Pumps",
    "Fire Pump Room Works",
    "Fire and Shaft doors",
    "Gas Reticulation System",
    "Softner - Electro Mechanical Works",
    "Hydro Pnematic Pumps",
    "Hardscape works",
    "Pergola & MS Works",
    "Irrigation",
    "Softscape works",
    "Entrance Gate Finishes & Boom barrier",
    "Play Area (shuttel,squash,indoor games,Basket ball,tennis)",
    "Entrance Road Works & Tower Hordings",
    "Peripheral Road Works outside the site",
    "Carparking works, Signages & Name Plates",
    "Club House MEP Works",
    "Swimming Pool - Equipment",
    "Club House Interiors & Exteriors",
    "Swimming pool Finishes incl Pergola",
    "Gym Equipment",
    "Loose Furniture",
    "QA/QC & QS Consultancy",
    "Lighting Consultant"
]

def patch_data():
    with open('/tmp/patch_log.txt', 'w') as log:
        try:
            log.write("Starting patch...\n")
            
            # Use frappe.db.sql to be absolutely sure we get records safely
            records = frappe.db.sql("""
                SELECT name, work_package, block, is_template, project_type 
                FROM `tabTender Calendar`
            """, as_dict=True)
            
            log.write(f"Total records found in DB: {len(records)}\n")
            
            # Step 1: Identify all Master records.
            # A master record is one that does not have a block assigned, 
            # OR is explicitly marked as a template.
            # (Generated sub-towers have block assigned and are NOT templates)
            master_records = [r for r in records if not r.get("block") or r.get("is_template")]
            log.write(f"Identified {len(master_records)} Master Records.\n")
            
            # Step 2: Assign sequence based on exact WORK_PACKAGES_ORDER
            next_unassigned_seq = len(WORK_PACKAGES_ORDER) + 1.0
            
            # Dictionary to map master's work_package to its exact float sl_no
            master_seq_map = {}
            
            for m in master_records:
                wp = (m.get("work_package") or "").strip()
                
                # Try to find exact match in the user's provided list
                # Since trailing spaces might be an issue, we match stripped versions
                matched_index = -1
                for idx, expected_wp in enumerate(WORK_PACKAGES_ORDER):
                    if wp == expected_wp.strip():
                        matched_index = idx
                        break
                        
                if matched_index != -1:
                    seq = float(matched_index + 1)
                else:
                    # If not in the user's explicit list (like 'test wp')
                    seq = float(next_unassigned_seq)
                    next_unassigned_seq += 1.0
                
                master_seq_map[wp] = seq
                frappe.db.sql("UPDATE `tabTender Calendar` SET sl_no = %s WHERE name = %s", (seq, m.name))
                log.write(f"MASTER: {wp} -> sl_no = {seq}\n")

            # Step 3: Identify and Assign generated Tower Wise records (the sub-records)
            sub_records = [r for r in records if r.get("block") and not r.get("is_template")]
            log.write(f"Identified {len(sub_records)} Sub-Tower Records.\n")
            
            # We want to group sub_records by their master
            # A sub record's work package usually looks like: "Master WP - Tower A"
            # We can map them by checking which master work_package string they start with
            for m_wp, m_seq in master_seq_map.items():
                if not m_wp:
                    continue
                # Find all sub-records for this master
                my_subs = [r for r in sub_records if r.get("work_package", "").startswith(m_wp + " -")]
                
                if my_subs:
                    # Sort them by creation or block name just to be safe
                    my_subs.sort(key=lambda x: x.get("block") or "")
                    
                    sub_seq_adder = 0.1
                    for sub in my_subs:
                        final_sub_seq = round(m_seq + sub_seq_adder, 1)
                        frappe.db.sql("UPDATE `tabTender Calendar` SET sl_no = %s WHERE name = %s", (final_sub_seq, sub.name))
                        log.write(f"  SUB: {sub.get('work_package')} -> sl_no = {final_sub_seq}\n")
                        sub_seq_adder += 0.1

            frappe.db.commit()
            log.write("Patch successfully completed!\n")
            
        except Exception as e:
            frappe.db.rollback()
            import traceback
            log.write(f"Error: {str(e)}\n{traceback.format_exc()}\n")
