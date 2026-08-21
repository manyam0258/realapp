import frappe


def execute():
    updated = 0
    already_correct = 0

    units = frappe.get_all(
        "Unit",
        fields=["name", "status"],
    )

    for unit in units:

        # If there is any non-cancelled Sales Booking Data
        # for this Unit, the Unit must be Sold.
        active_exists = frappe.db.exists(
            "Sales Booking Data",
            {
                "flat_no": unit.name,
                "status": ["!=", "Cancelled"],
            },
        )

        expected_status = "Sold" if active_exists else "Available"

        if unit.status != expected_status:

            frappe.db.set_value(
                "Unit",
                unit.name,
                "status",
                expected_status,
                update_modified=False,
            )

            frappe.logger().info(
                f"[Unit Status Fix V2] "
                f"{unit.name}: {unit.status} -> {expected_status}"
            )

            updated += 1

        else:
            already_correct += 1

    frappe.db.commit()

    frappe.logger().info(
        f"""
================ UNIT STATUS FIX V2 ================
Units Checked   : {len(units)}
Updated         : {updated}
Already Correct : {already_correct}
====================================================
"""
    )