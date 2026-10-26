from frappe import _

def get_data(doc=None):
    items = []
    if doc:
        if doc.fulfillment_type in ["Purchase Order", "Both"]:
            items.append("Purchase Order")
        if doc.fulfillment_type in ["Purchase Receipt", "Both"]:
            items.append("Purchase Receipt")
    else:
        items = ["Purchase Order", "Purchase Receipt"]

    return {
        "fieldname": "custom_procurement_contract",
        "transactions": [
            {
                "label": _("Fulfillment"),
                "items": items,
            }
        ],
    }