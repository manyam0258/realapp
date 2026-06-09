# Copyright (c) 2026, surendhranath and contributors
# For license information, please see license.txt

from datetime import timedelta
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class Tender(Document):

    def validate(self):
        if self.order_type == "Service":
            self.indigenous_import = "NA"
        if self.name and self.name.startswith("TEN-"):
            self.custom_sno = int(self.name.replace("TEN-", ""))
        if self.initiated_date and self.no_of_days_planned:
            self.target_date = self.add_working_days(
                getdate(self.initiated_date),
                int(self.no_of_days_planned)
            )
        if self.target_date and self.boq_submission_days_planned:
            self.boq_submission_target_date = self.add_working_days(
                getdate(self.target_date),
                int(self.boq_submission_days_planned)
            )
        if self.boq_submission_target_date and self.introduction_meeting_days_planned:
            self.vendor_evaluation_target_date = self.add_working_days(
                getdate(self.boq_submission_target_date),
                int(self.introduction_meeting_days_planned)
            )
        if self.vendor_evaluation_target_date and self.floating_enquiries_days_planned:
            self.floating_enquiries_target_date = self.add_working_days(
                getdate(self.vendor_evaluation_target_date),
                int(self.floating_enquiries_days_planned)
            )
        if self.floating_enquiries_target_date and self.pre_bid_no_of_days_planned:
            self.pre_bid_target_date = self.add_working_days(
                getdate(self.floating_enquiries_target_date),
                int(self.pre_bid_no_of_days_planned)
            )
        if self.pre_bid_target_date and self.quotation_1_days_planned:
            self.quotation_1_target_date = self.add_working_days(
                getdate(self.pre_bid_target_date),
                int(self.quotation_1_days_planned)
            )
        if self.quotation_1_target_date and self.quotation_2_days_planned:
            self.quotation_2_target_date = self.add_working_days(
                getdate(self.quotation_1_target_date),
                int(self.quotation_2_days_planned)
            )
        if self.quotation_2_target_date and self.order_approval_days_planned:
            self.order_approval_target_date = self.add_working_days(
                getdate(self.quotation_2_target_date),
                int(self.order_approval_days_planned)
            )
        if self.order_approval_target_date and self.agreement_no_of_days_planned:
            self.agreement_target_date = self.add_working_days(
                getdate(self.order_approval_target_date),
                int(self.agreement_no_of_days_planned)
            )
        if self.agreement_target_date and self.introduction_meeting_days_planned:
            self.introduction_meet_days_plan = self.add_working_days(
                getdate(self.agreement_target_date),
                int(self.introduction_meeting_days_planned)
            )
        self.design_sample_days_planned = self.no_of_days_planned
        self.design_sample_target_date = self.target_date

        if self.work_initiation and self.design_sample_target_date:
            self.duration_left = (
                getdate(self.design_sample_target_date)
                - getdate(self.work_initiation)
            ).days
        else:
            self.duration_left = 0

        if self.submission_date:
            self.submission_status = "Submitted"
        else:
            self.submission_status = "Yet to Submit"

        self.boq_no_of_days_planned = self.boq_submission_days_planned
        self.boq_target_date = self.boq_submission_target_date
        self.boq_work_initiation = self.submission_date

        if self.boq_work_initiation and self.boq_target_date:
            self.boq_duration_left = (
                getdate(self.boq_target_date)
                - getdate(self.boq_work_initiation)
            ).days
        else:
            self.boq_duration_left = 0
        if self.boq_submission_date:
            self.boq_submission_status = "Submitted"
        else:
            self.boq_submission_status = "Yet to Submit"

        self.vendor_evaluation_days_planned = self.introduction_meeting_days_planned
        self.vendor_target_date = self.vendor_evaluation_target_date
        self.vendor_evaluation_work_initiation = self.boq_submission_date
        if (
            self.vendor_evaluation_work_initiation
            and self.vendor_target_date
        ):
            self.vendor_evaluation_duration_left = (
                getdate(self.vendor_target_date)
                - getdate(self.vendor_evaluation_work_initiation)
            ).days
        else:
            self.vendor_evaluation_duration_left = 0
        if self.vendor_evaluation_submission_date:
            self.vendor_evaluation_submission_status = "Submitted"
        else:
            self.vendor_evaluation_submission_status = "Yet to Submit"
        self.introduction_days_planned = self.introduction_meeting_days_planned
        self.introduction_target_date = self.introduction_meet_days_plan
        self.introduction_work_initiation = self.agreement_order_submit_date
        if (
            self.introduction_work_initiation
            and self.introduction_target_date
        ):
            self.introduction_duration_left = (
                getdate(self.introduction_target_date)
                - getdate(self.introduction_work_initiation)
            ).days
        else:
            self.introduction_duration_left = 0
        if self.introduction_submission_date:
            self.introduction_submission_status = "Submitted"
        else:
            self.introduction_submission_status = "Yet to Submit"
        self.set_ref_no()
    def add_working_days(self, start_date, days):
        current_date = start_date
        added_days = 0
        while added_days < days:
            current_date += timedelta(days=1)
            if current_date.weekday() != 6:
                added_days += 1
        return current_date
    def set_ref_no(self):
        if self.data_reference == "Tender Calender":
            if not self.custom_work_package:
                frappe.throw(_("Work Package is mandatory for Tender Calender"))
            if self.is_new() or not self.ref_no:
                existing = frappe.get_all(
                    "Tender",
                    filters={
                        "custom_work_package": self.custom_work_package
                    },
                    pluck="ref_no"
                )
                max_no = 0
                for ref in existing:
                    if ref and ref.startswith(f"{self.custom_work_package}-"):
                        try:
                            num = int(ref.split("-")[-1])
                            max_no = max(max_no, num)
                        except Exception:
                            pass
                self.ref_no = f"{self.custom_work_package}-{max_no + 1}"
        elif self.data_reference == "Order Request Mail":
            if not self.ref_no:
                frappe.throw(
                    _("Ref No is mandatory when Data Reference is Order Request Mail")
                )