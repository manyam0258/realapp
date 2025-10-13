import frappe
from frappe.utils import flt

def execute():
    """
    Recalculate all financial fields in Unit after adding documentation_charges
    and unit_base_amount. Ensures existing records stay consistent with new logic.
    """

    frappe.logger().info("🔁 Starting full recalculation of Unit financial fields (including documentation_charges).")

    settings = frappe.get_single("Realapp Settings")

    # Fetch all Unit records
    units = frappe.get_all("Unit", fields=[
        "name",
        "salable_area",
        "basic_price_per_sft",
        "floor_rise_rate",
        "facing_premium_charges",
        "corner_premium_charges",
        "car_parking_amount",
        "documentation_charges",
        "amenities_charges_per_sft",
        "infra_charges_per_sft",
        "gst_rate",
        "tds_rate"
    ])

    total = len(units)
    updated = 0

    for u in units:
        area        = flt(u.salable_area or 0)
        base_rate   = flt(u.basic_price_per_sft or 0)
        rise_rate   = flt(u.floor_rise_rate or 0)
        facing_rate = flt(u.facing_premium_charges or 0)
        corner_rate = flt(u.corner_premium_charges or 0)
        car_park    = flt(u.car_parking_amount or 0)
        doc_charge  = flt(u.documentation_charges or 0)

        # If missing documentation_charges, pull from Realapp Settings
        if not doc_charge:
            doc_charge = flt(settings.get("default_documentation_charges") or 0)

        amen_rate   = flt(u.amenities_charges_per_sft or 0)
        infra_rate  = flt(u.infra_charges_per_sft or 0)

        gst_rate    = flt(u.gst_rate or settings.gst_rate or 5)
        tds_rate    = flt(u.tds_rate or settings.tds_rate or 1)

        if area <= 0:
            continue

        # --------------------------
        # Recalculation Logic
        # --------------------------

        unit_base = flt(area * base_rate, 2)

        full_unit_value = flt(
            (area * (base_rate + rise_rate + facing_rate + corner_rate))
            + car_park + doc_charge,
            2
        )

        value_excluding_bp = flt(
            (area * (rise_rate + facing_rate + corner_rate))
            + car_park + doc_charge,
            2
        )

        aos_value = flt((base_rate * area) + value_excluding_bp, 2)
        aos_gst = flt((aos_value * gst_rate) / 100, 2)
        aos_value_gst = flt(aos_value + aos_gst, 2)
        tds_amount = flt(aos_value * (tds_rate / 100), 2)
        net_payable = flt(aos_value_gst - tds_amount, 2)
        eff_rate = flt(net_payable / area, 2)

        # --------------------------
        # Update values in DB
        # --------------------------
        frappe.db.set_value("Unit", u.name, {
            "unit_base_amount": unit_base,
            "full_unit_value": full_unit_value,
            "value_excluding_bp": value_excluding_bp,
            "aos_value": aos_value,
            "aos_gst": aos_gst,
            "aos_value_gst": aos_value_gst,
            "tds_amount": tds_amount,
            "net_payable": net_payable,
            "effective_rate_per_sft": eff_rate,
            "documentation_charges": doc_charge
        })

        updated += 1

    frappe.db.commit()
    frappe.logger().info(f"✅ Recalculated {updated}/{total} Unit records with new documentation_charges logic.")
