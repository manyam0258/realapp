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

        # Check workflow transitions to set submission dates automatically or validate send back remarks
        db_state = self.get_db_value("workflow_state")
        if db_state and self.workflow_state and db_state != self.workflow_state:
            today_str = frappe.utils.today()
            if self.workflow_state == "BOQ Submission" and db_state == "Design Sample / Drawings":
                if not self.submission_date:
                    self.submission_date = today_str
            elif self.workflow_state == "Order Closure" and db_state == "BOQ Submission":
                if not self.boq_submission_date:
                    self.boq_submission_date = today_str
            elif self.workflow_state == "Vendor Finalisation" and db_state == "Order Closure":
                for field in [
                    "vendor_evaluation_submission_date",
                    "floating_enquiries_submission_date",
                    "pre_bid_technical_meeting_submission_date",
                    "negotiations_1_submit_date",
                    "negotiations_2_submit_date",
                    "order_approval_submit_date",
                    "agreement_order_submit_date"
                ]:
                    if not getattr(self, field):
                        setattr(self, field, today_str)
            elif self.workflow_state == "Completed" and db_state == "Vendor Finalisation":
                for field in ["introduction_submission_date", "mobilization_submit_date"]:
                    if not getattr(self, field):
                        setattr(self, field, today_str)

            # Handle revision status increment on Send Back transitions
            self.update_revision_status_on_sendback(db_state)

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
        if self.introduction_meet_days_plan and self.mobilization_days_planned:
            self.mobilization_target_date = self.add_working_days(
                getdate(self.introduction_meet_days_plan),
                int(self.mobilization_days_planned)
            )

        self.design_sample_days_planned = self.no_of_days_planned
        self.design_sample_target_date = self.target_date

        self.duration_left = self.get_duration_left_str(self.design_sample_target_date, self.work_initiation)

        if self.submission_date:
            self.submission_status = "Submitted"
        else:
            self.submission_status = "Yet to Submit"

        # Chaining of dates: work initiation of next stage = submission date of previous stage
        if self.submission_date:
            self.boq_work_initiation = self.submission_date
        if self.boq_submission_date:
            self.vendor_evaluation_work_initiation = self.boq_submission_date
        if self.vendor_evaluation_submission_date:
            self.floating_enquiries_work_initiation = self.vendor_evaluation_submission_date
        if self.floating_enquiries_submission_date:
            self.pre_bid_technical_meeting_work_initiation = self.floating_enquiries_submission_date
        if self.pre_bid_technical_meeting_submission_date:
            self.negotiations_1_work_initiation = self.pre_bid_technical_meeting_submission_date
        if self.negotiations_1_submit_date:
            self.negotiations_2_work_initiation = self.negotiations_1_submit_date
        if self.negotiations_2_submit_date:
            self.order_approval_work_initiation = self.negotiations_2_submit_date
        if self.order_approval_submit_date:
            self.agreement_order_work_initiation = self.order_approval_submit_date
        if self.agreement_order_submit_date:
            self.introduction_work_initiation = self.agreement_order_submit_date
        if self.introduction_submission_date:
            self.mobilization_work_initiation = self.introduction_submission_date

        self.boq_no_of_days_planned = self.boq_submission_days_planned
        self.boq_target_date = self.boq_submission_target_date


        self.boq_duration_left = self.get_duration_left_str(self.boq_target_date, self.boq_work_initiation)
        if self.boq_submission_date:
            self.boq_submission_status = "Submitted"
        else:
            self.boq_submission_status = "Yet to Submit"

        self.vendor_evaluation_days_planned = self.introduction_meeting_days_planned
        self.vendor_target_date = self.vendor_evaluation_target_date
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

        # Stage 4: Floating Enquiries
        self.floating_enquiries_no_of_days_planned = self.floating_enquiries_days_planned
        self.floating_enquiries_target = self.floating_enquiries_target_date
        if not self.floating_enquiries_work_initiation or self.has_value_changed("vendor_evaluation_submission_date"):
            self.floating_enquiries_work_initiation = self.vendor_evaluation_submission_date
        self.floating_enquiries_duration_left = self.get_duration_left_str(self.floating_enquiries_target, self.floating_enquiries_work_initiation)
        if self.floating_enquiries_submission_date:
            self.floating_enquiries_submission_status = "Submitted"
        else:
            self.floating_enquiries_submission_status = "Yet to Submit"

        # Stage 5: Pre-Bid / Technical Meeting
        self.pre_bid_technical_meeting_no_of_days_planned = self.pre_bid_no_of_days_planned
        self.pre_bid_technical_meeting_target_date = self.pre_bid_target_date
        if not self.pre_bid_technical_meeting_work_initiation or self.has_value_changed("floating_enquiries_submission_date"):
            self.pre_bid_technical_meeting_work_initiation = self.floating_enquiries_submission_date
        self.pre_bid_technical_meeting_duration_left = self.get_duration_left_str(self.pre_bid_technical_meeting_target_date, self.pre_bid_technical_meeting_work_initiation)
        if self.pre_bid_technical_meeting_submission_date:
            self.pre_bid_technical_meeting_submission_status = "Submitted"
        else:
            self.pre_bid_technical_meeting_submission_status = "Yet to Submit"

        # Stage 6: Negotiations 1
        self.negotiations_1_days_plan = self.quotation_1_days_planned
        self.negotiations_1_target_date = self.quotation_1_target_date
        if not self.negotiations_1_work_initiation or self.has_value_changed("pre_bid_technical_meeting_submission_date"):
            self.negotiations_1_work_initiation = self.pre_bid_technical_meeting_submission_date
        self.negotiations_1_duration_left = self.get_duration_left_str(self.negotiations_1_target_date, self.negotiations_1_work_initiation)
        if self.negotiations_1_submit_date:
            self.negotiations_1_submit_status = "Submitted"
        else:
            self.negotiations_1_submit_status = "Yet to Submit"

        # Stage 7: Negotiations 2
        self.negotiations_2_days_plan = self.quotation_2_days_planned
        self.negotiations_2_target_date = self.quotation_2_target_date
        if not self.negotiations_2_work_initiation or self.has_value_changed("negotiations_1_submit_date"):
            self.negotiations_2_work_initiation = self.negotiations_1_submit_date
        self.negotiations_2_duration_left = self.get_duration_left_str(self.negotiations_2_target_date, self.negotiations_2_work_initiation)
        if self.negotiations_2_submit_date:
            self.negotiations_2_submit_status = "Submitted"
        else:
            self.negotiations_2_submit_status = "Yet to Submit"

        # Stage 8: Order Approval
        self.order_approval_days = self.order_approval_days_planned
        self.order_approval_target = self.order_approval_target_date
        if not self.order_approval_work_initiation or self.has_value_changed("negotiations_2_submit_date"):
            self.order_approval_work_initiation = self.negotiations_2_submit_date
        self.order_approval_duration_left = self.get_duration_left_str(self.order_approval_target, self.order_approval_work_initiation)
        if self.order_approval_submit_date:
            self.order_approval_submit_status = "Submitted"
        else:
            self.order_approval_submit_status = "Yet to Submit"

        # Stage 9: Agreement Order
        self.agreement_order_days_planned = self.agreement_no_of_days_planned
        self.agreement_order_target_date = self.agreement_target_date
        if not self.agreement_order_work_initiation or self.has_value_changed("order_approval_submit_date"):
            self.agreement_order_work_initiation = self.order_approval_submit_date
        self.agreement_order_duration_left = self.get_duration_left_str(self.agreement_order_target_date, self.agreement_order_work_initiation)
        if self.agreement_order_submit_date:
            self.agreement_order_submission = "Submitted"
        else:
            self.agreement_order_submission = "Yet to Submit"

        # Stage 10: Introduction Meeting
        self.introduction_days_planned = self.introduction_meeting_days_planned
        self.introduction_target_date = self.introduction_meet_days_plan
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

        # Stage 11: Mobilization
        if not self.mobilization_work_initiation or self.has_value_changed("introduction_submission_date"):
            self.mobilization_work_initiation = self.introduction_submission_date
        self.mobilization_duration_left = self.get_duration_left_str(self.mobilization_target_date, self.mobilization_work_initiation)
        if self.mobilization_submit_date:
            self.mobilization_submit_status = "Submitted"
        else:
            self.mobilization_submit_status = "Yet to Submit"
        self.set_ref_no()
        self.calculate_revised_target_dates()

    def get_duration_left_str(self, target_date, work_initiation):
        if target_date and work_initiation:
            diff = (getdate(target_date) - getdate(work_initiation)).days
            if diff >= 0:
                return f"{diff} days left" if diff != 1 else "1 day left"
            else:
                return f"{abs(diff)} days delayed" if abs(diff) != 1 else "1 day delayed"
        return "0 days left"
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

    def update_revision_status_on_sendback(self, previous_state):
        """Update revision status when document is sent back to a previous workflow state."""
        # Map each state to its revision status field
        revision_fields = {
            "Tender Creation": "revision_status",
            "Design Sample / Drawings": "revision_status",
            "BOQ Submission": "boq_revision_status",
            "Order Closure": "vendor_evaluation_revision_status",
            "Vendor Finalisation": "introduction_revision_status"
        }

        # Determine which revision status field to update based on target state
        current_state = self.workflow_state
        if current_state in revision_fields:
            fieldname = revision_fields[current_state]
            if self._was_sent_back_to(current_state):
                # Get current revision status and increment
                current_status = getattr(self, fieldname, None) or "R0"
                revision_levels = ["R0", "R1", "R2", "R3", "R4"]
                current_idx = revision_levels.index(current_status) if current_status in revision_levels else 0
                if current_idx < len(revision_levels) - 1:
                    setattr(self, fieldname, revision_levels[current_idx + 1])

    def _was_sent_back_to(self, target_state):
        """Check if the document was sent back (not forward) to the target state."""
        # The workflow transition is a send back if the target state is earlier in the workflow
        # States in order: Tender Creation < Design Sample / Drawings < BOQ Submission < Order Closure < Vendor Finalisation < Completed
        state_order = {
            "Tender Creation": 1,
            "Design Sample / Drawings": 2,
            "BOQ Submission": 3,
            "Order Closure": 4,
            "Vendor Finalisation": 5,
            "Completed": 6
        }
        db_state = self.get_db_value("workflow_state")
        if db_state and db_state in state_order and target_state in state_order:
            return state_order[target_state] < state_order[db_state]
        return False

    def calculate_revised_target_dates(self):
        """Calculate revised target dates based on work initiation dates."""
        # Revised target dates: work_initiation + days_planned
        # Tab 2: Schematic Readiness
        if self.work_initiation and self.no_of_days_planned:
            self.revised_planned_date = self.add_working_days(
                getdate(self.work_initiation),
                int(self.no_of_days_planned)
            )

        # Tab 3: BOQ Submission
        if self.boq_work_initiation and self.boq_submission_days_planned:
            self.revised_date = self.add_working_days(
                getdate(self.boq_work_initiation),
                int(self.boq_submission_days_planned)
            )

        # Tab 4: Order Closure - Vendor Evaluation
        if self.vendor_evaluation_work_initiation and self.introduction_meet_days_planned:
            self.vendor_evaluation_revised_planned_date = self.add_working_days(
                getdate(self.vendor_evaluation_work_initiation),
                int(self.introduction_meet_days_planned)
            )

        # Tab 4: Floating Enquiries
        if self.floating_enquiries_work_initiation and self.floating_enquiries_days_planned:
            self.floating_enquiries_revised_planned_date = self.add_working_days(
                getdate(self.floating_enquiries_work_initiation),
                int(self.floating_enquiries_days_planned)
            )

        # Tab 4: Pre-Bid Technical Meeting
        if self.pre_bid_technical_meeting_work_initiation and self.pre_bid_no_of_days_planned:
            self.pre_bid_technical_meeting_revised_planned_date = self.add_working_days(
                getdate(self.pre_bid_technical_meeting_work_initiation),
                int(self.pre_bid_no_of_days_planned)
            )

        # Tab 4: Negotiations 1
        if self.negotiations_1_work_initiation and self.quotation_1_days_planned:
            self.negotiations_1_rev_plan_date = self.add_working_days(
                getdate(self.negotiations_1_work_initiation),
                int(self.quotation_1_days_planned)
            )

        # Tab 4: Negotiations 2
        if self.negotiations_2_work_initiation and self.quotation_2_days_planned:
            self.negotiations_2_rev_plan_date = self.add_working_days(
                getdate(self.negotiations_2_work_initiation),
                int(self.quotation_2_days_planned)
            )

        # Tab 4: Order Approval
        if self.order_approval_work_initiation and self.order_approval_days_planned:
            self.order_approval_revised_date = self.add_working_days(
                getdate(self.order_approval_work_initiation),
                int(self.order_approval_days_planned)
            )

        # Tab 5: Agreement Order
        if self.agreement_order_work_initiation and self.agreement_no_of_days_planned:
            self.agreement_order_revised_plan_date = self.add_working_days(
                getdate(self.agreement_order_work_initiation),
                int(self.agreement_no_of_days_planned)
            )

        # Tab 5: Introduction Meeting
        if self.introduction_work_initiation and self.introduction_meeting_days_planned:
            self.introduction_revised_planned_date = self.add_working_days(
                getdate(self.introduction_work_initiation),
                int(self.introduction_meeting_days_planned)
            )

        # Tab 5: Mobilization
        if self.mobilization_work_initiation and self.mobilization_days_planned:
            self.mobilization_revised_planned_date = self.add_working_days(
                getdate(self.mobilization_work_initiation),
                int(self.mobilization_days_planned)
            )