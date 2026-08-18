# Copyright (c) 2026, surendhranath and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate


class TestTender(FrappeTestCase):
	def test_tender_date_calculations_from_vendor_evaluation_onward(self):
		tender = frappe.new_doc("Tender")
		tender.data_reference = "Order Request Mail"
		tender.ref_no = "REF-TEST-001"
		tender.initiated_date = "2026-08-10"
		tender.no_of_days_planned = 5
		tender.boq_submission_days_planned = 5
		tender.introduction_meet_days_planned = 5
		tender.floating_enquiries_days_planned = 4
		tender.pre_bid_no_of_days_planned = 3
		tender.quotation_1_days_planned = 5
		tender.quotation_2_days_planned = 2
		tender.order_approval_days_planned = 4
		tender.agreement_no_of_days_planned = 3
		tender.introduction_meeting_days_planned = 2
		tender.mobilization_days_planned = 5
		tender.vendor_days_planned = 5

		tender.save()

		# Stage 1: Schematic Target (2026-08-10 + 5 working days) = 2026-08-15
		self.assertEqual(str(tender.target_date), "2026-08-15")
		self.assertEqual(str(tender.design_sample_target_date), "2026-08-15")
		self.assertEqual(tender.design_sample_days_planned, 5)

		# Stage 2: BOQ Target (2026-08-15 + 5 working days, skipping Sun 16) = 2026-08-21
		self.assertEqual(str(tender.boq_submission_target_date), "2026-08-21")
		self.assertEqual(str(tender.boq_target_date), "2026-08-21")
		self.assertEqual(tender.boq_no_of_days_planned, 5)

		# Stage 3: Vendor Evaluation Target (2026-08-21 + 5 working days, skipping Sun 23) = 2026-08-27
		self.assertEqual(str(tender.vendor_evaluation_target_date), "2026-08-27")
		self.assertEqual(str(tender.vendor_target_date), "2026-08-27")
		self.assertEqual(tender.vendor_evaluation_days_planned, 5)

		# Stage 4: Floating Enquiries Target (2026-08-27 + 4 working days, skipping Sun 30) = 2026-09-01
		self.assertEqual(str(tender.floating_enquiries_target_date), "2026-09-01")
		self.assertEqual(str(tender.floating_enquiries_target), "2026-09-01")
		self.assertEqual(tender.floating_enquiries_no_of_days_planned, 4)

		# Stage 5: Pre-Bid Target (2026-09-01 + 3 working days) = 2026-09-04
		self.assertEqual(str(tender.pre_bid_target_date), "2026-09-04")
		self.assertEqual(str(tender.pre_bid_technical_meeting_target_date), "2026-09-04")
		self.assertEqual(tender.pre_bid_technical_meeting_no_of_days_planned, 3)

		# Stage 6: Quotation 1 Target (2026-09-04 + 5 working days, skipping Sun 06) = 2026-09-10
		self.assertEqual(str(tender.quotation_1_target_date), "2026-09-10")
		self.assertEqual(str(tender.negotiations_1_target_date), "2026-09-10")
		self.assertEqual(tender.negotiations_1_days_plan, 5)

		# Stage 7: Quotation 2 Target (2026-09-10 + 2 working days, skipping Sun 13 if applicable) = 2026-09-12
		self.assertEqual(str(tender.quotation_2_target_date), "2026-09-12")
		self.assertEqual(str(tender.negotiations_2_target_date), "2026-09-12")
		self.assertEqual(tender.negotiations_2_days_plan, 2)

		# Stage 8: Order Approval Target (2026-09-12 + 4 working days, skipping Sun 13) = 2026-09-17
		self.assertEqual(str(tender.order_approval_target_date), "2026-09-17")
		self.assertEqual(str(tender.order_approval_target), "2026-09-17")
		self.assertEqual(tender.order_approval_days, 4)

		# Stage 9: Agreement Target (2026-09-17 + 3 working days, skipping Sun 20) = 2026-09-21
		self.assertEqual(str(tender.agreement_target_date), "2026-09-21")
		self.assertEqual(str(tender.agreement_order_target_date), "2026-09-21")
		self.assertEqual(tender.agreement_order_days_planned, 3)

		# Stage 10: Introduction Meeting Target (2026-09-21 + 2 working days) = 2026-09-23
		self.assertEqual(str(tender.introduction_meet_days_plan), "2026-09-23")
		self.assertEqual(str(tender.introduction_target_date), "2026-09-23")
		self.assertEqual(tender.introduction_days_planned, 2)

		# Stage 11: Mobilization Target (2026-09-23 + 5 working days, skipping Sun 27) = 2026-09-29
		self.assertEqual(str(tender.vendor_mobilization_target_date), "2026-09-29")
		self.assertEqual(str(tender.mobilization_target_date), "2026-09-29")
		self.assertEqual(tender.mobilization_days_planned, 5)

		# Reload document from database to verify persistence on Save/Reopen
		reloaded = frappe.get_doc("Tender", tender.name)
		self.assertEqual(str(reloaded.vendor_evaluation_target_date), "2026-08-27")
		self.assertEqual(str(reloaded.vendor_target_date), "2026-08-27")
		self.assertEqual(reloaded.vendor_evaluation_days_planned, 5)
		self.assertEqual(str(reloaded.floating_enquiries_target_date), "2026-09-01")
		self.assertEqual(str(reloaded.pre_bid_target_date), "2026-09-04")
		self.assertEqual(str(reloaded.quotation_1_target_date), "2026-09-10")
		self.assertEqual(str(reloaded.quotation_2_target_date), "2026-09-12")
		self.assertEqual(str(reloaded.order_approval_target_date), "2026-09-17")
		self.assertEqual(str(reloaded.agreement_target_date), "2026-09-21")
		self.assertEqual(str(reloaded.introduction_meet_days_plan), "2026-09-23")
		self.assertEqual(str(reloaded.vendor_mobilization_target_date), "2026-09-29")
		self.assertEqual(str(reloaded.mobilization_target_date), "2026-09-29")
		self.assertEqual(reloaded.mobilization_days_planned, 5)

	def test_revised_target_date_calculation(self):
		tender = frappe.new_doc("Tender")
		tender.data_reference = "Order Request Mail"
		tender.ref_no = "REF-TEST-002"
		tender.work_initiation = "2026-08-10"
		tender.no_of_days_planned = 15
		tender.boq_work_initiation = "2026-08-10"
		tender.boq_submission_days_planned = 10
		tender.save()

		# Revised Target Date = Work Initiation Date + No. of Days Planned
		# 2026-08-10 + 15 working days (skipping Sundays Aug 16 & Aug 23) = 2026-08-27
		self.assertEqual(str(tender.revised_planned_date), "2026-08-27")

		# 2026-08-10 + 10 working days (skipping Sunday Aug 16) = 2026-08-21
		self.assertEqual(str(tender.revised_date), "2026-08-21")

	def test_timeline_status_calculation(self):
		today = frappe.utils.today()
		future_date = frappe.utils.add_days(today, 3)
		past_date = frappe.utils.add_days(today, -3)

		tender = frappe.new_doc("Tender")
		tender.data_reference = "Order Request Mail"
		tender.ref_no = "REF-TEST-003"

		# Test Days Left
		self.assertEqual(tender.get_duration_left_str(future_date), "3 Days Left")

		# Test Due Today
		self.assertEqual(tender.get_duration_left_str(today), "Due Today")

		# Test Days Delayed
		self.assertEqual(tender.get_duration_left_str(past_date), "3 Days Delayed")
