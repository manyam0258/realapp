import frappe


def execute():
    status_map = {
        "Token Amount Paid": "Booked",
        "10% Paid": "Booked",
        "20% Paid": "Booked",
        "Confirmed": "Booked",
        "AOS Done": "Sold",
        "Cancelled": "Available",
    }

    updated = 0
    already_correct = 0
    skipped = 0

    units = frappe.db.sql(
        """
        SELECT DISTINCT flat_no
        FROM `tabSales Booking Data`
        WHERE flat_no IS NOT NULL
        """,
        as_dict=True,
    )

    for unit in units:

        # Skip orphan records
        if not frappe.db.exists("Unit", unit.flat_no):
            skipped += 1
            continue

        sbds = frappe.get_all(
            "Sales Booking Data",
            filters={"flat_no": unit.flat_no},
            fields=["name", "status", "creation"],
            order_by="creation desc",
        )

        if not sbds:
            skipped += 1
            continue

        # Use latest active booking.
        # If every booking is Cancelled, use the latest Cancelled booking.
        active_sbds = [s for s in sbds if s.status != "Cancelled"]

        if active_sbds:
            latest = active_sbds[0]
        else:
            latest = sbds[0]

        expected_status = status_map.get(latest.status)

        if not expected_status:
            skipped += 1
            continue

        current_status = frappe.db.get_value(
            "Unit",
            unit.flat_no,
            "status",
        )

        if current_status != expected_status:
            frappe.db.set_value(
                "Unit",
                unit.flat_no,
                "status",
                expected_status,
                update_modified=False,
            )

            frappe.logger().info(
                f"[Unit Status Fix] {unit.flat_no}: "
                f"{current_status} -> {expected_status} "
                f"(SBD: {latest.name}, {latest.status})"
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
Skipped         : {skipped}
================================================
"""
    )