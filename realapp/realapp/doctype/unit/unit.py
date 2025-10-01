# Copyright (c) 2025
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

class Unit(Document):
    def validate(self):
        self.set_floor_number()
        self.apply_defaults()
        self.calculate_dynamic_fields()

    def set_floor_number(self):
        """Auto fetch floor_number from Floor if not set (Floor.floor)."""
        if self.floor and not self.floor_number:
            self.floor_number = frappe.db.get_value("floor", self.floor, "floor") or 0

    def apply_defaults(self):
        """Unit overrides > Settings > 0"""
        settings = frappe.get_single("Realapp Settings")

        def pick(fieldname):
            return self.get(fieldname) if self.get(fieldname) not in (None, "") else settings.get(fieldname) or 0

        self.basic_price_per_sft        = pick("base_price_per_sft")
        self.floor_rise_rate            = pick("floor_rise_rate")
        self.facing_premium_charges     = pick("facing_premium_charges")
        self.corner_premium_charges     = pick("corner_premium_charges")
        self.car_parking_amount         = pick("car_parking_amount")

        # also bring per-sft infra/amenities for info amounts
        self.amenities_charges_per_sft  = pick("amenities_charges_per_sft")
        self.infra_charges_per_sft      = pick("infra_charges_per_sft")

        # tax rates for display / js preview
        self.gst_rate = settings.gst_rate
        self.tds_rate = settings.tds_rate

    def calculate_dynamic_fields(self):
        area          = flt(self.salable_area or 0)
        base_rate     = flt(self.basic_price_per_sft or 0)
        rise_rate     = flt(self.floor_rise_rate or 0)
        facing_rate   = flt(self.facing_premium_charges or 0)
        corner_rate   = flt(self.corner_premium_charges or 0)
        car_parking   = flt(self.car_parking_amount or 0)

        # informational amounts (not included in Full/AOS per your Excel)
        amen_rate     = flt(self.amenities_charges_per_sft or 0)
        infra_rate    = flt(self.infra_charges_per_sft or 0)

        gst_rate      = flt(self.gst_rate or 5)
        tds_rate      = flt(self.tds_rate or 1)

        # If no area, zero out everything
        if area <= 0:
            self.amenities_charges_amt = 0
            self.infra_charges_amt = 0
            self.full_unit_value = 0
            self.value_excluding_bp = 0
            self.aos_value = 0
            self.aos_value_gst = 0
            self.tds_amount = 0
            self.net_payable = 0
            self.effective_rate_per_sft = 0
            return

        # Calculate informational amounts
        self.amenities_charges_amt = flt(amen_rate * area, 2)
        self.infra_charges_amt     = flt(infra_rate * area, 2)

        # ---- Excel rules you shared ----
        # Full Unit Value = area * (base + rise + facing + corner) + car parking
        self.full_unit_value = flt(area * (base_rate + rise_rate + facing_rate + corner_rate) + car_parking, 2)

        # Value Excluding Base Price = area * (rise + facing + corner) + car parking
        self.value_excluding_bp = flt(area * (rise_rate + facing_rate + corner_rate) + car_parking, 2)

        # AOS Value = (base_rate * area) + value_excluding_bp
        self.aos_value = flt((base_rate * area) + self.value_excluding_bp, 2)

        # GST and TDS on AOS
        self.aos_value_gst = flt(self.aos_value * (1 + gst_rate / 100), 2)
        self.tds_amount    = flt(self.aos_value * (tds_rate / 100), 2)

        # Net payable and effective per sft
        self.net_payable = flt(self.aos_value_gst - self.tds_amount, 2)
        self.effective_rate_per_sft = flt(self.net_payable / area, 2)
