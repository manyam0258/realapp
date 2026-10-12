import frappe
from frappe import _


def validate_items(doc, method=None):
    for row in doc.items:
        if not row.qty or row.qty <= 0:
            frappe.throw(
                _("Row #{0}: Quantity for item {1} must be greater than zero.").format(
                    row.idx, row.item_code
                ),
                title=_("Invalid Quantity"),
            )

        # Free items are exempt from the rate check
        if not row.get("is_free_item") and (row.rate is None or row.rate <= 0):
            frappe.throw(
                _("Row #{0}: Rate for item {1} is required and must be greater than zero.").format(
                    row.idx, row.item_code
                ),
                title=_("Rate Required"),
            )
