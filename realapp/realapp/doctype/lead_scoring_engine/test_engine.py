import frappe
from frappe.tests.utils import FrappeTestCase
from realapp.realapp.doctype.lead_scoring_engine.engine import LeadScoringEngine

class TestLeadScoringEngine(FrappeTestCase):
    def setUp(self):
        # Create dummy Project
        self.project = frappe.get_doc({
            "doctype": "Project",
            "project_name": "Test Project",
            "latitude": 12.9716,
            "longitude": 77.5946
        }).insert(ignore_permissions=True)

        # Create dummy Lead Scoring Parameter
        if not frappe.db.exists("Lead Scoring Parameter", "Test Income"):
            frappe.get_doc({
                "doctype": "Lead Scoring Parameter",
                "parameter_name": "Test Income",
                "dimension": "Financial", # Assuming this exists or needs creation
                "scoring_logic_type": "Range",
                "field_reference": "annual_income",
                "default_weightage": 10,
                "max_score": 10,
                "active": 1
            }).insert(ignore_permissions=True)

        # Create dummy Lead Scoring Template
        self.template = frappe.get_doc({
            "doctype": "Lead Scoring Template",
            "template_name": "Test Template",
            "project": self.project.name,
            "status": "Active",
            "details": [
                {
                    "parameter": "Test Income",
                    "weightage": 10,
                    "max_score": 10,
                    "criteria": "500000", # Threshold
                    "active": 1
                }
            ]
        }).insert(ignore_permissions=True)

        # Create dummy Lead
        self.lead = frappe.get_doc({
            "doctype": "Lead",
            "lead_name": "Test Lead",
            "annual_income": 600000,
            "latitude": 12.9716,
            "longitude": 77.5946
        }).insert(ignore_permissions=True)

    def tearDown(self):
        frappe.db.rollback()

    def test_evaluate_range_rule(self):
        engine = LeadScoringEngine(self.template.name)
        
        # Test Income > 500000 (Lead has 600000)
        # We need to mock get_parameter_definition or rely on DB
        # Since we inserted it, it should work.
        
        # Manually trigger evaluate_lead
        # Total possible score is 10
        report = engine.evaluate_lead(self.lead, 10)
        
        self.assertEqual(report["total_score"], 100.0)
        self.assertEqual(report["category"], "Hot")

    def test_evaluate_match_rule(self):
        # Create a Match parameter
        if not frappe.db.exists("Lead Scoring Parameter", "Test City"):
            frappe.get_doc({
                "doctype": "Lead Scoring Parameter",
                "parameter_name": "Test City",
                "dimension": "Demographics", 
                "scoring_logic_type": "Match",
                "field_reference": "city",
                "max_score": 20,
                "active": 1
            }).insert(ignore_permissions=True)
            
        # Add to template
        self.template.append("details", {
            "parameter": "Test City",
            "weightage": 20,
            "max_score": 20,
            "criteria": "Bangalore",
            "active": 1
        })
        self.template.save()
        
        self.lead.city = "Bangalore"
        self.lead.save()
        
        engine = LeadScoringEngine(self.template.name)
        # Total score now 10 + 20 = 30
        report = engine.evaluate_lead(self.lead, 30)
        
        self.assertEqual(report["total_score"], 100.0)

    def test_evaluate_geodistance(self):
        # Create Geo parameter
        if not frappe.db.exists("Lead Scoring Parameter", "Test Geo"):
            frappe.get_doc({
                "doctype": "Lead Scoring Parameter",
                "parameter_name": "Test Geo",
                "dimension": "Demographics",
                "scoring_logic_type": "GeoDistance",
                "max_score": 50,
                "active": 1
            }).insert(ignore_permissions=True)
            
        self.template.append("details", {
            "parameter": "Test Geo",
            "weightage": 50,
            "max_score": 50,
            "criteria": "10", # 10 km radius
            "active": 1
        })
        self.template.save()
        
        # Lead is at same location as project (dist=0)
        engine = LeadScoringEngine(self.template.name)
        # Total score 10 + 50 = 60 (ignoring previous match test for simplicity of this unit)
        # Actually template persists, so it has Income(10) + Geo(50) = 60.
        # Lead has Income(Pass) + Geo(Pass) = 60/60 = 100%
        
        report = engine.evaluate_lead(self.lead, 60)
        self.assertEqual(report["total_score"], 100.0)
        
        # Move lead far away
        self.lead.latitude = 20.0
        self.lead.save()
        
        report = engine.evaluate_lead(self.lead, 60)
        # Income(10) + Geo(0) = 10/60 = 16.67%
        self.assertLess(report["total_score"], 20.0)

