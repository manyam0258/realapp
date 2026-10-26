# Copyright (c) 2026, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc


class ProcurementContract(Document):
    pass


@frappe.whitelist()
def make_purchase_order(source_name, target_doc=None):
    contract = frappe.get_doc("Procurement Contract", source_name)

    # Validate that this contract allows Purchase Order generation
    if contract.fulfillment_type not in ["Purchase Order", "Both"]:
        frappe.throw(_("This contract is not configured to create Purchase Orders."))

    def set_missing_values(source, target):
        if source.party_type == "Supplier":
            target.supplier = source.party_name
        target.custom_procurement_contract = source.name

    doclist = get_mapped_doc(
        "Procurement Contract",
        source_name,
        {
            "Procurement Contract": {
                "doctype": "Purchase Order",
                "validation": {
                    "docstatus": ["=", 1]
                },
            },
            # Maps schedule child table items into Purchase Order items
            "Procurement Contract Schedule Item": {
                "doctype": "Purchase Order Item",
                "field_map": {
                    "item_code": "item_code",
                    "qty": "qty",
                    "rate": "rate",
                    "to_date": "schedule_date",
                },
                # Only map rows that have an item_code defined
                "condition": lambda doc: doc.item_code is not None,
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist


@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
    contract = frappe.get_doc("Procurement Contract", source_name)

    # Validate that this contract allows Purchase Receipt generation
    if contract.fulfillment_type not in ["Purchase Receipt", "Both"]:
        frappe.throw(_("This contract is not configured to create Purchase Receipts."))

    def set_missing_values(source, target):
        if source.party_type == "Supplier":
            target.supplier = source.party_name
        target.custom_procurement_contract = source.name

    doclist = get_mapped_doc(
        "Procurement Contract",
        source_name,
        {
            "Procurement Contract": {
                "doctype": "Purchase Receipt",
                "validation": {
                    "docstatus": ["=", 1]
                },
            },
            # Maps schedule child table items into Purchase Receipt items
            "Procurement Contract Schedule Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "item_code": "item_code",
                    "qty": "qty",
                    "rate": "rate",
                },
                # Only map rows that have an item_code defined
                "condition": lambda doc: doc.item_code is not None,
            },
        },
        target_doc,
        set_missing_values,
    )

    return doclist