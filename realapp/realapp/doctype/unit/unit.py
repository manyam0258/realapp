# Copyright (c) 2025
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class Unit(Document):
    def validate(self):
        # Ensure hierarchy & defaults before calculations
        self.set_hierarchy()
        self.apply_defaults()
        self.calculate_dynamic_fields()
    
    def set_hierarchy(self):
        """Auto-fill Block, Project, Floor Number from Floor"""
        if self.floor_name:
            floor_doc = frappe.get_doc("Floor", self.floor_name)   # user selected floor_name (Link)

            # Block from Floor
            if floor_doc.block:
                self.block = floor_doc.block
                block_doc = frappe.get_doc("Block", floor_doc.block)
                if block_doc.project:
                    self.project = block_doc.project

            # Floor Number (Int) from Floor
            if hasattr(floor_doc, "floor_number") and floor_doc.floor_number is not None:
                self.floor_number = floor_doc.floor_number
            else:
                self.floor_number = 0

    def apply_defaults(self):
        """Fill defaults from Realapp Settings only if field is empty (not 0)"""
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
            current_val = self.get(unit_field)
            # only override if field is empty, not when it's explicitly 0
            if current_val in (None, ""):
                self.set(unit_field, settings.get(settings_field) or 0)

        # tax rates always synced from settings
        self.gst_rate = settings.gst_rate
        self.tds_rate = settings.tds_rate

    def calculate_dynamic_fields(self):
        """Compute amounts based on Excel rules"""
        area          = flt(self.salable_area or 0)
        base_rate     = flt(self.basic_price_per_sft or 0)
        rise_rate     = flt(self.floor_rise_rate or 0)
        facing_rate   = flt(self.facing_premium_charges or 0)
        corner_rate   = flt(self.corner_premium_charges or 0)
        car_parking   = flt(self.car_parking_amount or 0)

        # informational amounts
        amen_rate     = flt(self.amenities_charges_per_sft or 0)
        infra_rate    = flt(self.infra_charges_per_sft or 0)

        gst_rate      = flt(self.gst_rate or 5)
        tds_rate      = flt(self.tds_rate or 1)

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
            return

        # ---- Informational amounts ----
        self.amenities_charges_amt   = flt(amen_rate * area, 2)
        self.infra_charges_amt       = flt(infra_rate * area, 2)
        self.floor_rise_charges_amt  = flt(rise_rate * area, 2)

        # ---- Excel rules ----
        # Full Unit Value
        self.full_unit_value = flt(
            (area * (base_rate + rise_rate + facing_rate + corner_rate)) + car_parking,
            2
        )

        # Value Excluding Base Price
        self.value_excluding_bp = flt(
            (area * (rise_rate + facing_rate + corner_rate)) + car_parking,
            2
        )

        # AOS Value
        self.aos_value = flt((base_rate * area) + self.value_excluding_bp, 2)

        # GST on AOS
        self.aos_gst = flt((self.aos_value * gst_rate) / 100, 2)

        # AOS + GST
        self.aos_value_gst = flt(self.aos_value + self.aos_gst, 2)

        # TDS
        self.tds_amount = flt(self.aos_value * (tds_rate / 100), 2)

        # Net payable and effective per sft
        self.net_payable = flt(self.aos_value_gst - self.tds_amount, 2)
        self.effective_rate_per_sft = flt(self.net_payable / area, 2)
