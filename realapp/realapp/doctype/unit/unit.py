# Copyright (c) 2025
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt
from frappe.model.mapper import get_mapped_doc


class Unit(Document):
    def validate(self):
        # Ensure hierarchy & defaults before calculations
        self.set_hierarchy()
        self.apply_defaults()
        self.calculate_dynamic_fields()

        # Ensure status always has a valid default
        if not self.status:
            self.status = "Available"

    # ------------------------------
    # Hierarchy / Defaults
    # ------------------------------
    def set_hierarchy(self):
        """Auto-fill Block, Project, Floor Number from Floor"""
        if self.floor_name:
            floor_doc = frappe.get_doc("Floor", self.floor_name)

            if floor_doc.block:
                self.block = floor_doc.block
                block_doc = frappe.get_doc("Block", floor_doc.block)
                if block_doc.project:
                    self.project = block_doc.project

            self.floor_number = getattr(floor_doc, "floor_number", 0) or 0

    def apply_defaults(self):
        """Fill defaults from Realapp Settings only if field is empty"""
        settings = frappe.get_single("Realapp Settings")

        mapping = {
            "base_price_per_sft": "basic_price_per_sft",
            "floor_rise_rate": "floor_rise_rate",
            "facing_premium_charges": "facing_premium_charges",
            "corner_premium_charges": "corner_premium_charges",
            "car_parking_amount": "car_parking_amount",
            "amenities_charges_per_sft": "amenities_charges_per_sft",
            "infra_charges_per_sft": "infra_charges_per_sft",
        }

        for settings_field, unit_field in mapping.items():
            if self.get(unit_field) in (None, ""):
                self.set(unit_field, settings.get(settings_field) or 0)

        # --- NEW ---
        # Default documentation charges from Realapp Settings if empty
        if not self.documentation_charges:
            self.documentation_charges = flt(settings.get("default_documentation_charges") or 0)

        # Always sync tax rates
        self.gst_rate = settings.gst_rate
        self.tds_rate = settings.tds_rate

    # ------------------------------
    # Calculations
    # ------------------------------
    def calculate_dynamic_fields(self):
        """Compute amounts based on Excel rules"""
        area        = flt(self.salable_area or 0)
        base_rate   = flt(self.basic_price_per_sft or 0)
        rise_rate   = flt(self.floor_rise_rate or 0)
        facing_rate = flt(self.facing_premium_charges or 0)
        corner_rate = flt(self.corner_premium_charges or 0)
        car_parking = flt(self.car_parking_amount or 0)
        doc_charges = flt(self.documentation_charges or 0)  # --- NEW ---

        amen_rate   = flt(self.amenities_charges_per_sft or 0)
        infra_rate  = flt(self.infra_charges_per_sft or 0)

        gst_rate    = flt(self.gst_rate or 5)
        tds_rate    = flt(self.tds_rate or 1)

        if area <= 0:
            self.amenities_charges_amt = 0
            self.infra_charges_amt = 0
            self.floor_rise_charges_amt = 0
            self.full_unit_value = 0
            self.value_excluding_bp = 0
            self.aos_value = 0
            self.aos_gst = 0
            self.aos_value_gst = 0
            self.tds_amount = 0
            self.net_payable = 0
            self.effective_rate_per_sft = 0
            self.unit_base_amount = 0
            return

        self.amenities_charges_amt = flt(amen_rate * area, 2)
        self.infra_charges_amt = flt(infra_rate * area, 2)
        self.floor_rise_charges_amt = flt(rise_rate * area, 2)
        self.facing_premium_amount = flt(facing_rate * area, 2)
        self.corner_premium_amount = flt(corner_rate * area, 2)


        # --- NEW ---
        self.unit_base_amount = flt(area * base_rate, 2)

        # Include documentation charges in total computation
        self.full_unit_value = flt(
            (area * (base_rate + rise_rate + facing_rate + corner_rate + amen_rate + infra_rate)) + doc_charges, 2
        )
        self.value_excluding_bp = flt(
            (area * (rise_rate + facing_rate + corner_rate + amen_rate + infra_rate)) + car_parking + doc_charges, 2
        )

        self.aos_value = flt((base_rate * area) + self.value_excluding_bp, 2)

        self.aos_gst = flt((self.aos_value * gst_rate) / 100, 2)
        self.aos_value_gst = flt(self.aos_value + self.aos_gst, 2)
        self.tds_amount = flt(self.aos_value * (tds_rate / 100), 2)

        self.net_payable = flt(self.aos_value_gst - self.tds_amount, 2)
        self.effective_rate_per_sft = flt(self.net_payable / area, 2)

    # ------------------------------
    # Status Lifecycle
    # ------------------------------
    def mark_as_booked(self):
        if self.status in ["Booked", "Sold"]:
            frappe.throw(f"Unit {self.name} is already {self.status}.")
        if self.status == "Blocked":
            frappe.throw(f"Unit {self.name} is Blocked and cannot be booked.")
        self.status = "Booked"
        self.save()

    def mark_as_blocked(self):
        if self.status in ["Booked", "Sold"]:
            frappe.throw(f"Unit {self.name} is already {self.status}.")
        self.status = "Blocked"
        self.save()

    def mark_as_available(self):
        if self.status == "Sold":
            frappe.throw(f"Unit {self.name} is already Sold.")
        self.status = "Available"
        self.save()

    def mark_as_sold(self):
        if self.status != "Booked":
            frappe.throw(f"Unit {self.name} must be Booked before Sold.")
        self.status = "Sold"
        self.save()


# ------------------------------
# Whitelisted: Create Cost Sheet from Unit
# ------------------------------
@frappe.whitelist()
def make_cost_sheet(source_name, target_doc=None):
    """Map Unit → Cost Sheet (used by Create button)."""

    def postprocess(source, target):
        # Link back to Unit
        target.unit = source.name
        target.project = source.project
        target.block = source.block
        target.floor_number = source.floor_number
        target.salable_area = source.salable_area

        # Copy pricing & computed fields
        target.basic_price_per_sft = source.basic_price_per_sft
        target.value_excluding_bp = source.value_excluding_bp
        target.full_unit_value = source.full_unit_value
        target.aos_value = source.aos_value
        target.aos_gst = source.aos_gst
        target.aos_value_gst = source.aos_value_gst
        target.tds_amount = source.tds_amount
        target.net_payable = source.net_payable
        target.effective_rate_per_sft = source.effective_rate_per_sft

    return get_mapped_doc(
        "Unit",
        source_name,
        {
            "Unit": {
                "doctype": "Cost Sheet",
                "field_map": {"name": "unit"},
                "field_no_map": ["naming_series"],
            }
        },
        target_doc,
        postprocess,
    )
