import frappe


def execute():

    updated = 0
    already_correct = 0

    units = frappe.get_all(
        "Unit",
        fields=["name", "status"],
    )

    for unit in units:

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
                f"[Unit Status Fix] {unit.name}: "
                f"{unit.status} -> {expected_status}"
            )

            updated += 1

        else:
            already_correct += 1

    frappe.db.commit()

    frappe.logger().info(
        f"""
================ UNIT STATUS FIX ================
Units Checked   : {len(units)}
Updated         : {updated}
Already Correct : {already_correct}
================================================
"""
    )