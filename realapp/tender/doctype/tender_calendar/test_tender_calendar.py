# Copyright (c) 2026, surendhranath and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days, date_diff
from realapp.tender.doctype.tender_calendar.tender_calendar import get_calendar_events, generate_tower_tenders

class TestTenderCalendar(FrappeTestCase):
    def setUp(self):
        # Setup test data
        self.project_name = "PROJ-0023"
        
        # Ensure Tender Settings allow cascading
        settings = frappe.get_single("Tender Settings")
        settings.enable_cascading = 1
        settings.default_mode = "Auto"
        settings.save()
        
        # Cleanup existing test records for this project if any
        self.cleanup_test_records()

    def tearDown(self):
        self.cleanup_test_records()
        frappe.db.rollback()

    def cleanup_test_records(self):
        frappe.flags.skip_sequence_shift = True
        existing = frappe.get_all("Tender Calendar", filters={"project": self.project_name})
        for record in existing:
            frappe.delete_doc("Tender Calendar", record.name, force=True)
        frappe.flags.skip_sequence_shift = False

    def test_autoname_and_insert(self):
        """Test that the sequence sl_no is auto-generated and gantt_title is populated."""
        t1 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 1",
            "boq_submission_date": "2026-06-01",
            "tender_issue_date": "2026-06-05",
            "approval_date": "2026-06-10",
            "contract_date": "2026-06-15",
            "mobilization_date": "2026-06-20",
            "target_date": "2026-06-25",
            "cascading_mode": "Auto"
        })
        t1.insert()
        
        self.assertTrue(t1.sl_no >= 1.0)
        self.assertEqual(t1.gantt_title, f"{t1.sl_no} - Civil - Test WP 1")
        
    def test_cascading_auto(self):
        """Test that delaying the BOQ submission date cascades dates progressively in Auto mode."""
        t1 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 1",
            "boq_submission_date": "2026-06-01",
            "tender_issue_date": "2026-06-05",
            "approval_date": "2026-06-10",
            "contract_date": "2026-06-15",
            "mobilization_date": "2026-06-20",
            "target_date": "2026-06-25",
            "cascading_mode": "Auto"
        })
        t1.insert()
        
        # Save original dates
        orig_issue = t1.tender_issue_date
        orig_approval = t1.approval_date
        orig_contract = t1.contract_date
        orig_mobilization = t1.mobilization_date
        orig_target = t1.target_date
        
        # Shift BOQ submission date by 5 days
        t1.boq_submission_date = "2026-06-06"
        t1.save()
        
        # Reload and check shifts
        t1.reload()
        
        # Expecting:
        # tender_issue_date: +5 days
        # approval_date: +7 days (delta + 2)
        # contract_date: +10 days (delta + 5)
        # mobilization_date: +15 days (delta + 10)
        # target_date: +15 days (delta + 10)
        self.assertEqual(str(t1.tender_issue_date), str(add_days(orig_issue, 5)))
        self.assertEqual(str(t1.approval_date), str(add_days(orig_approval, 7)))
        self.assertEqual(str(t1.contract_date), str(add_days(orig_contract, 10)))
        self.assertEqual(str(t1.mobilization_date), str(add_days(orig_mobilization, 15)))
        self.assertEqual(str(t1.target_date), str(add_days(orig_target, 15)))

    def test_generate_tower_tenders(self):
        """Test the Tower Wise generation engine with partial selection and deletion resilience."""
        from realapp.tender.doctype.tender_calendar.tender_calendar import (
            get_remaining_blocks, generate_selected_tower_tenders
        )
        
        t1 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "project_type": "Tower Wise",
            "category": "Civil",
            "work_package": "Test WP 1",
            "boq_submission_date": "2026-06-01",
            "tender_issue_date": "2026-06-05",
            "approval_date": "2026-06-10",
            "contract_date": "2026-06-15",
            "mobilization_date": "2026-06-20",
            "target_date": "2026-06-25",
            "cascading_mode": "Auto"
        })
        t1.insert()
        
        # 1. Initially, all blocks should be remaining
        remaining = get_remaining_blocks(t1.name)
        self.assertEqual(len(remaining), 7)
        block_names = [b.name for b in remaining]
        self.assertIn("A", block_names)
        self.assertIn("G", block_names)
        
        # 2. Generate sub-tenders for only 3 blocks (A, B, C)
        status = generate_selected_tower_tenders(t1.name, ["A", "B", "C"])
        self.assertTrue(status)
        
        t1.reload()
        self.assertEqual(t1.is_template, 1)
        self.assertEqual(t1.towers_generated, 0) # Should be 0 since D, E, F, G are not generated yet
        
        # Check remaining blocks (should be 4 left: D, E, F, G)
        remaining = get_remaining_blocks(t1.name)
        self.assertEqual(len(remaining), 4)
        remaining_names = [b.name for b in remaining]
        self.assertEqual(sorted(remaining_names), ["D", "E", "F", "G"])
        
        # Verify A, B, C sub-tenders were created
        sub_tenders = frappe.get_all("Tender Calendar", 
                                     filters={"project": self.project_name, "work_package": ["like", "Test WP 1 - Tower%"]},
                                     fields=["name", "sl_no", "block", "project_type"])
        self.assertEqual(len(sub_tenders), 3)
        for sub in sub_tenders:
            self.assertTrue(sub.sl_no % 1 != 0)
            self.assertEqual(sub.project_type, "Project")
            
        # 3. Generate remaining 4 blocks
        status = generate_selected_tower_tenders(t1.name, ["D", "E", "F", "G"])
        self.assertTrue(status)
        
        t1.reload()
        self.assertEqual(t1.towers_generated, 1) # Now all blocks are generated, so it should be 1
        
        remaining = get_remaining_blocks(t1.name)
        self.assertEqual(len(remaining), 0)
        
        # 4. Test Deletion Resilience: Delete sub-tender for Block B
        sub_b = frappe.get_all("Tender Calendar", filters={
            "project": self.project_name,
            "block": "B",
            "work_package": "Test WP 1 - Tower - B"
        })
        self.assertEqual(len(sub_b), 1)
        
        frappe.delete_doc("Tender Calendar", sub_b[0].name)
        
        # Verify master's towers_generated is reset to 0
        t1.reload()
        self.assertEqual(t1.towers_generated, 0)
        
        # Verify block B is now back in remaining list
        remaining = get_remaining_blocks(t1.name)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].name, "B")


    def test_sequence_trash_handling(self):
        """Test sequence re-ordering when a record is deleted."""
        # Insert 3 records
        t1 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 1",
            "cascading_mode": "Manual"
        }).insert()
        
        t2 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 2",
            "cascading_mode": "Manual"
        }).insert()
        
        t3 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 3",
            "cascading_mode": "Manual"
        }).insert()
        
        # Verify sequence numbers
        s1, s2, s3 = t1.sl_no, t2.sl_no, t3.sl_no
        self.assertEqual(s2, s1 + 1)
        self.assertEqual(s3, s2 + 1)
        
        # Delete t2
        frappe.delete_doc("Tender Calendar", t2.name)
        
        # Reload t3 and check sequence
        t3.reload()
        self.assertEqual(t3.sl_no, s3 - 1)

    def test_calendar_events_retrieval(self):
        """Test get_calendar_events endpoint structure."""
        t1 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 1",
            "pre_bid_date": "2026-06-02",
            "tender_issue_date": "2026-06-05",
            "approval_date": "2026-06-10",
            "contract_date": "2026-06-15",
            "mobilization_date": "2026-06-20",
            "target_date": "2026-06-25",
            "cascading_mode": "Manual"
        }).insert()
        
        events = get_calendar_events("2026-06-01", "2026-06-30", filters={"project": self.project_name})
        
        # There should be 5 events for our inserted package (Pre-Bid, Issue, Approval, Contract, Mobilization)
        wp_events = [e for e in events if e["name"] == t1.name]
        self.assertEqual(len(wp_events), 5)
        
        titles = [e["title"] for e in wp_events]
        self.assertIn("[Pre-Bid] Test WP 1", titles)
        self.assertIn("[Issue] Test WP 1", titles)
        self.assertIn("[Approval] Test WP 1", titles)
        self.assertIn("[Contract] Test WP 1", titles)
        self.assertIn("[Mobilization] Test WP 1", titles)

    def test_report_sorting(self):
        """Test that all specified reports sort their data by sl_no asc."""
        t1 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP 1",
            "boq_submission_date": "2026-06-01",
            "target_date": "2026-06-25",
            "status": "Finalised",
            "cascading_mode": "Manual"
        }).insert()
        
        t2 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Mechanical",
            "work_package": "Test WP 2",
            "boq_submission_date": "2026-05-01",
            "target_date": "2026-06-20",
            "status": "Finalised",
            "cascading_mode": "Manual"
        }).insert()
        
        t3 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Electrical",
            "work_package": "Test WP 3",
            "boq_submission_date": "2026-07-01",
            "target_date": "2026-06-30",
            "status": "Finalised",
            "cascading_mode": "Manual"
        }).insert()
        
        # Swap sl_no to ensure we test sorting order, not creation order
        t1.db_set("sl_no", 3.0)
        t2.db_set("sl_no", 1.0)
        t3.db_set("sl_no", 2.0)
        
        expected_wp_order = ["Test WP 2", "Test WP 3", "Test WP 1"]
        
        # 1. BOQ Status Report
        from realapp.tender.report.boq_status_report.boq_status_report import execute as execute_boq
        cols, data = execute_boq(filters={"project": self.project_name})
        wp_list = [d["work_package"] for d in data if d["work_package"] in expected_wp_order]
        self.assertEqual(wp_list, expected_wp_order)
        
        # 2. Quotation Status Report
        from realapp.tender.report.quotation_status_report.quotation_status_report import execute as execute_quotation
        cols, data = execute_quotation(filters={"project": self.project_name})
        wp_list = [d["work_package"] for d in data if d["work_package"] in expected_wp_order]
        self.assertEqual(wp_list, expected_wp_order)
        
        # 3. Order Status Report
        from realapp.tender.report.order_status_report.order_status_report import execute as execute_order
        cols, data = execute_order(filters={"project": self.project_name})
        wp_list = [d["work_package"] for d in data if d["work_package"] in expected_wp_order]
        self.assertEqual(wp_list, expected_wp_order)
        
        # 4. Combined Tracker
        from realapp.tender.report.combined_tracker.combined_tracker import execute as execute_combined
        cols, data = execute_combined(filters={"project": self.project_name})
        wp_list = [d["work_package"] for d in data if d["work_package"] in expected_wp_order]
        self.assertEqual(wp_list, expected_wp_order)
        
        # 5. Master Tender Calendar
        from realapp.tender.report.master_tender_calendar.master_tender_calendar import execute as execute_master
        cols, data, message, chart = execute_master(filters={"project": self.project_name})
        wp_list = [d["work_package"] for d in data if d["work_package"] in expected_wp_order]
        self.assertEqual(wp_list, expected_wp_order)

    def test_permission_restrictions(self):
        """Test that only planning roles can create Tender Calendar docs."""
        test_user_email = "test_perm_user@example.com"
        if frappe.db.exists("User", test_user_email):
            frappe.delete_doc("User", test_user_email, force=True)
            
        user = frappe.get_doc({
            "doctype": "User",
            "email": test_user_email,
            "first_name": "Test Permission User",
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        
        # Add 'Architect' role (read/write only, no create/delete)
        user.roles = []
        user.append("roles", {"role": "Architect"})
        user.save(ignore_permissions=True)
        
        frappe.clear_cache(user=test_user_email)
        frappe.set_user(test_user_email)
        
        doc = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP Perm Fail",
            "cascading_mode": "Manual"
        })
        
        self.assertRaises(frappe.PermissionError, doc.insert)
        
        frappe.set_user("Administrator")
        
        # Add 'Planning' role (which has full permissions including create/delete)
        user = frappe.get_doc("User", test_user_email)
        user.roles = []
        user.append("roles", {"role": "Planning"})
        user.save(ignore_permissions=True)
        
        frappe.clear_cache(user=test_user_email)
        frappe.set_user(test_user_email)
        
        doc2 = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP Perm Success",
            "cascading_mode": "Manual"
        })
        
        try:
            doc2.insert()
            self.assertTrue(frappe.db.exists("Tender Calendar", doc2.name))
        finally:
            frappe.set_user("Administrator")
            if doc2.get("name") and frappe.db.exists("Tender Calendar", doc2.name):
                frappe.delete_doc("Tender Calendar", doc2.name, force=True)
            frappe.delete_doc("User", test_user_email, force=True)

    def test_workflow_transitions(self):
        """Test that Tender Calendar workflow transitions states correctly using assigned roles."""
        doc = frappe.get_doc({
            "doctype": "Tender Calendar",
            "project": self.project_name,
            "category": "Civil",
            "work_package": "Test WP Workflow",
            "cascading_mode": "Manual"
        })
        doc.insert()
        self.assertEqual(doc.workflow_state, "Tender Creation")
        
        test_user_email = "test_wf_user@example.com"
        if frappe.db.exists("User", test_user_email):
            frappe.delete_doc("User", test_user_email, force=True)
            
        user = frappe.get_doc({
            "doctype": "User",
            "email": test_user_email,
            "first_name": "Test Workflow User",
            "send_welcome_email": 0
        })
        user.insert(ignore_permissions=True)
        
        # Test 1: Architect role cannot transition 'Tender Creation' -> 'Design Sample / Drawings'
        user.roles = []
        user.append("roles", {"role": "Architect"})
        user.save(ignore_permissions=True)
        frappe.clear_cache(user=test_user_email)
        frappe.set_user(test_user_email)
        
        from frappe.model.workflow import apply_workflow, WorkflowTransitionError
        self.assertRaises(WorkflowTransitionError, apply_workflow, doc, "Send for Design")
        
        # Test 2: Planning role can transition 'Tender Creation' -> 'Design Sample / Drawings'
        frappe.set_user("Administrator")
        user = frappe.get_doc("User", test_user_email)
        user.roles = []
        user.append("roles", {"role": "Planning"})
        user.save(ignore_permissions=True)
        frappe.clear_cache(user=test_user_email)
        frappe.set_user(test_user_email)
        
        doc = frappe.get_doc("Tender Calendar", doc.name)
        apply_workflow(doc, "Send for Design")
        self.assertEqual(doc.workflow_state, "Design Sample / Drawings")
        
        # Test 3: Planning role cannot transition 'Design Sample / Drawings' -> 'BOQ Submission' (only Architect can)
        self.assertRaises(WorkflowTransitionError, apply_workflow, doc, "Submit Design")
        
        # Test 4: Architect role can transition 'Design Sample / Drawings' -> 'BOQ Submission'
        frappe.set_user("Administrator")
        user = frappe.get_doc("User", test_user_email)
        user.roles = []
        user.append("roles", {"role": "Architect"})
        user.save(ignore_permissions=True)
        frappe.clear_cache(user=test_user_email)
        frappe.set_user(test_user_email)
        
        doc = frappe.get_doc("Tender Calendar", doc.name)
        apply_workflow(doc, "Submit Design")
        self.assertEqual(doc.workflow_state, "BOQ Submission")
        
        # Revert user to Administrator and clean up
        frappe.set_user("Administrator")
        frappe.delete_doc("Tender Calendar", doc.name, force=True)
        frappe.delete_doc("User", test_user_email, force=True)

def run_tests():
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTenderCalendar)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        raise Exception("Some tests failed!")
    print("All tests passed successfully!")
