# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CostSheet(Document):

    def validate(self):
        """Main validation entrypoint."""
        self.set_project_hierarchy()
        self.apply_basic_price_logic()
        self.calculate_before_registration_charges()
        self.calculate_totals()

    # -------------------------------------------------
    # Project Hierarchy
    # -------------------------------------------------
    def set_project_hierarchy(self):
        """Auto-set project, block, floor from selected Unit"""
        if not self.unit:
            return

        unit = frappe.get_doc("Unit", self.unit)

        # Traverse: Unit -> Floor -> Block -> Project
        floor = frappe.get_doc("Floor", unit.floor) if unit.floor else None
        block = frappe.get_doc("Block", floor.block) if floor and floor.block else None

        self.floor = unit.floor
        if hasattr(unit, "floor_no"):
            self.floor_no = unit.floor_no

        self.block = block.name if block else None
        self.project = block.project if block else None

        # Pull important Unit details
        self.carpet_area = unit.carpet_area
        if hasattr(unit, "builtup_area"):
            self.builtup_area = unit.builtup_area
        self.balcony_area = unit.balcony_area
        self.uds = unit.uds
        self.facing = unit.facing
        self.corner_preference = unit.corner_preference
        self.basic_price_per_sft = unit.basic_price_per_sft

    # -------------------------------------------------
    # Basic Price Logic
    # -------------------------------------------------
    def apply_basic_price_logic(self):
        """Apply cost sheet type logic (Standard vs Negotiated)"""
        if self.cost_sheet_type == "Standard":
            # always take from Unit
            unit = frappe.get_doc("Unit", self.unit)
            self.basic_price_per_sft = unit.basic_price_per_sft
        elif self.cost_sheet_type == "Negotiated":
            # allow sales user to override self.basic_price_per_sft manually
            if not self.basic_price_per_sft:
                frappe.throw("Please enter Basic Price for Negotiated Cost Sheet")

    # -------------------------------------------------
    # Before Registration Charges
    # -------------------------------------------------
    def calculate_before_registration_charges(self):
        """Calculate charges payable before registration"""
        settings = frappe.get_single("Realapp Settings")
        salable_area = self.carpet_area or 0

        # Maintenance (with GST)
        maintenance_rate = settings.maintenance_rate_per_sft or 0
        maintenance_total = maintenance_rate * salable_area
        maintenance_gst_rate = settings.maintenance_gst_rate or 0
        maintenance_gst = maintenance_total * (maintenance_gst_rate / 100)

        # Corpus
        corpus_rate = settings.corpus_fund_rate_per_sft or 0
        corpus_total = corpus_rate * salable_area

        # Fixed values
        refundable = settings.refundable_caution_deposit or 0
        move_in = settings.move_in_charges or 0
        registration = settings.default_registration_charges or 0

        # Save to fields on Cost Sheet
        self.maintenance_total = maintenance_total + maintenance_gst
        self.corpus_fund_total = corpus_total
        self.refundable_caution_deposit = refundable
        self.move_in_charges = move_in
        self.registration_charges = registration

        # Overall total
        self.before_registration_total = (
            self.maintenance_total
            + self.corpus_fund_total
            + self.refundable_caution_deposit
            + self.move_in_charges
            + self.registration_charges
        )

    # -------------------------------------------------
    # Totals (Agreement + GST + TDS)
    # -------------------------------------------------
    def calculate_totals(self):
        """Compute agreement value and net payable"""
        unit = frappe.get_doc("Unit", self.unit)
        settings = frappe.get_single("Realapp Settings")

        salable_area = unit.area_in_sft or 0
        base_price = (self.basic_price_per_sft or 0) * salable_area

        infra_amt = (settings.infra_charges_per_sft or 0) * salable_area
        amenities_amt = (settings.amenities_charges_per_sft or 0) * salable_area

        full_value = (
            base_price
            + infra_amt
            + amenities_amt
            + (unit.floor_rise_charges or 0)
            + (unit.facing_premium_charges or 0)
            + (unit.corner_premium_charges or 0)
            + (unit.car_parking_amount or 0)
            + (settings.documentation_charges or 0)
        )

        self.agreement_value = full_value

        gst_rate = settings.gst_rate or 5
        self.gst_amount = full_value * (gst_rate / 100)

        self.grand_total_payable = (
            self.agreement_value
            + self.gst_amount
            + self.before_registration_total
        )
