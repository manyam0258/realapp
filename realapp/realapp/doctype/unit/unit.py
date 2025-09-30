# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Unit(Document):
    def validate(self):
        """ On validate, populate dynamic calculated fields """
        self.apply_defaults()
        self.calculate_dynamic_fields()

    def apply_defaults(self):
        """ If Unit field is missing, fetch from Realapp Settings """
        settings = frappe.get_single("Realapp Settings")

        def get_value(field):
            return self.get(field) or settings.get(field) or 0

        # Apply defaults if not set
        self.basic_price_per_sft = get_value("base_price_per_sft")
        self.facing_premium_charges = get_value("facing_premium_charges")
        self.corner_premium_charges = get_value("corner_premium_charges")
        self.car_parking_amount = get_value("car_parking_amount")
        self.amenities_charges_per_sft = get_value("amenities_charges_per_sft")
        self.infra_charges_per_sft = get_value("infra_charges_per_sft")
        self.documentation_charges = get_value("documentation_charges")

        # Store GST/TDS for reference
        self.gst_rate = settings.gst_rate or 5
        self.tds_rate = settings.tds_rate or 1

        # Base floor rise rate (used for calculation only)
        self.floor_rise_rate = settings.floor_rise_rate or 20

    def calculate_dynamic_fields(self):
        """ Compute all derived values """
        salable_area = self.area_in_sft or 0
        base_price = (self.basic_price_per_sft or 0) * salable_area
        infra_amt = (self.infra_charges_per_sft or 0) * salable_area
        amenities_amt = (self.amenities_charges_per_sft or 0) * salable_area

        self.amenities_charges_amt = amenities_amt
        self.infra_charges_amt = infra_amt

        # 🔹 Floor Rise Calculation
        floor_number = 0
        if self.floor:
            floor_number = frappe.db.get_value("Floor", self.floor, "floor_number") or 0

        if self.is_floor_rise_applicable and floor_number >= 5:
            multiplier = floor_number - 4
            effective_rate = multiplier * self.floor_rise_rate
            self.effective_floor_rise_rate = effective_rate
            self.floor_rise_charges = effective_rate * salable_area
        else:
            self.effective_floor_rise_rate = 0
            self.floor_rise_charges = 0

        # Full value = base + add-ons
        full_value = (
            base_price
            + infra_amt
            + amenities_amt
            + (self.floor_rise_charges or 0)
            + (self.facing_premium_charges or 0)
            + (self.corner_premium_charges or 0)
            + (self.car_parking_amount or 0)
            + (self.documentation_charges or 0)
        )
        self.full_unit_value = full_value

        # Value excluding base price (just add-ons)
        self.value_excluding_bp = (
            infra_amt
            + amenities_amt
            + (self.floor_rise_charges or 0)
            + (self.facing_premium_charges or 0)
            + (self.corner_premium_charges or 0)
            + (self.car_parking_amount or 0)
            + (self.documentation_charges or 0)
        )

        # Agreement of Sale (AOS) value
        self.aos_value = full_value

        # AOS + GST
        gst_rate = self.gst_rate or 5
        self.aos_value_gst_5 = full_value * (1 + gst_rate / 100)

        # TDS
        tds_rate = self.tds_rate or 1
        self.tds_1 = full_value * (tds_rate / 100)

        # Net payable
        self.net_payable = self.aos_value_gst_5 - self.tds_1
