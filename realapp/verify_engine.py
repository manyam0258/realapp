import frappe
from realapp.realapp.doctype.lead_scoring_engine.engine import LeadScoringEngine

def verify():
    try:
        frappe.db.rollback()
        
        # 1. Setup Data
        # Project
        if not frappe.db.exists("Project", "Verify Project"):
            project = frappe.get_doc({
                "doctype": "Project",
                "project_name": "Verify Project",
                "latitude": 12.9716,
                "longitude": 77.5946
            }).insert()
        else:
            project = frappe.get_doc("Project", "Verify Project")

        # Parameter: Income (Range)
        if not frappe.db.exists("Lead Scoring Parameter", "Verify Income"):
            frappe.get_doc({
                "doctype": "Lead Scoring Parameter",
                "parameter_name": "Verify Income",
                "dimension": "Financial", # Ensure this exists or use a string if it's not a Link
                "scoring_logic_type": "Range",
                "field_reference": "annual_income",
                "default_weightage": 50,
                "max_score": 50,
                "active": 1
            }).insert()

        # Parameter: City (Match)
        if not frappe.db.exists("Lead Scoring Parameter", "Verify City"):
            frappe.get_doc({
                "doctype": "Lead Scoring Parameter",
                "parameter_name": "Verify City",
                "dimension": "Demographics",
                "scoring_logic_type": "Match",
                "field_reference": "city",
                "default_weightage": 50,
                "max_score": 50,
                "active": 1
            }).insert()

        # Template
        if not frappe.db.exists("Lead Scoring Template", "Verify Template"):
            template = frappe.get_doc({
                "doctype": "Lead Scoring Template",
                "template_name": "Verify Template",
                "project": project.name,
                "status": "Active",
                "details": [
                    {
                        "parameter": "Verify Income",
                        "weightage": 50,
                        "max_score": 50,
                        "criteria": "500000", # Threshold
                        "active": 1
                    },
                    {
                        "parameter": "Verify City",
                        "weightage": 50,
                        "max_score": 50,
                        "criteria": "Bangalore",
                        "active": 1
                    }
                ]
            }).insert()
        else:
            template = frappe.get_doc("Lead Scoring Template", "Verify Template")

        # Lead 1: Hot (Income > 5L, City = Bangalore)
        lead1 = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Verify Lead 1",
            "first_name": "Verify Lead 1",
            "annual_income": 600000,
            "city": "Bangalore"
        }).insert(ignore_permissions=True)

        # Lead 2: Cold (Income < 5L, City = Mumbai)
        lead2 = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Verify Lead 2",
            "first_name": "Verify Lead 2",
            "annual_income": 400000,
            "city": "Mumbai"
        }).insert(ignore_permissions=True)

        frappe.db.commit()

        # 2. Run Engine
        print("Running Lead Scoring Engine...")
        engine = LeadScoringEngine(template.name)
        engine.generate_reports()

        # 3. Verify Results
        report1 = frappe.db.get_value("Lead Scoring Report", {"lead": lead1.name, "lead_scoring_template": template.name}, ["total_score", "category"], as_dict=True)
        report2 = frappe.db.get_value("Lead Scoring Report", {"lead": lead2.name, "lead_scoring_template": template.name}, ["total_score", "category"], as_dict=True)

        print(f"Lead 1 Report: {report1}")
        print(f"Lead 2 Report: {report2}")

        if report1.total_score == 100.0 and report1.category == "Hot":
            print("PASS: Lead 1 scored correctly.")
        else:
            print("FAIL: Lead 1 score incorrect.")

        if report2.total_score == 0.0 and report2.category == "Cold":
            print("PASS: Lead 2 scored correctly.")
        else:
            print("FAIL: Lead 2 score incorrect.")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        # frappe.db.rollback() # Uncomment to rollback changes
        pass

verify()
