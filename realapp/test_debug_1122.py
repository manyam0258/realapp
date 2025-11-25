import frappe
from realapp.realapp.doctype.lead_scoring_engine.engine import LeadScoringEngine

def test_test1122():
    """Debug Test1122 template scoring"""
    
    # Get the lead
    lead = frappe.get_doc("Lead", "CRM-LEAD-2025-00001")
    
    print("=" * 80)
    print("LEAD DATA:")
    print("=" * 80)
    print(f"Name: {lead.name}")
    print(f"Lead Name: {lead.lead_name}")
    print(f"Employment Type: {lead.employment_type} (type: {type(lead.employment_type)})")
    print(f"Marital Status: {lead.marital_status} (type: {type(lead.marital_status)})")
    print(f"Age: {lead.lead_age} (type: {type(lead.lead_age)})")
    print(f"Annual Income: {lead.annual_income} (type: {type(lead.annual_income)})")
    print(f"Loan Pre-approved: {lead.loan_preapproved} (type: {type(lead.loan_preapproved)})")
    print(f"Existing Property Owner: {lead.existing_property_owner} (type: {type(lead.existing_property_owner)})")
    print(f"Has Kids: {lead.has_kids} (type: {type(lead.has_kids)})")
    print(f"Site Visit Scheduled: {lead.site_visit_scheduled} (type: {type(lead.site_visit_scheduled)})")
    print(f"Last Contact Days: {lead.last_contact_days} (type: {type(lead.last_contact_days)})")
    print(f"Purchase Timeline: {lead.purchase_timeline} (type: {type(lead.purchase_timeline)})")
    print(f"Decision Maker Type: {lead.decision_maker_type} (type: {type(lead.decision_maker_type)})")
    print(f"Urgency Reason: {lead.urgency_reason} (type: {type(lead.urgency_reason)})")
    print(f"Lead Latitude: {lead.lead_latitude}")
    print(f"Lead Longitude: {lead.lead_longitude}")
    
    print("\n" + "=" * 80)
    print("TESTING ENGINE:")
    print("=" * 80)
    
    # Test engine
    engine = LeadScoringEngine("Test1122")
    template = engine.template
    project = engine.project
    
    print(f"Template: {template.name}")
    print(f"Project: {project.name}")
    print(f"Project Lat: {project.latitude}, Lon: {project.longitude}")
    
    # Test each rule individually
    print("\n" + "=" * 80)
    print("RULE-BY-RULE EVALUATION:")
    print("=" * 80)
    
    for rule in template.details:
        if not rule.active:
            continue
            
        param_def = engine.get_parameter_definition(rule.parameter)
        if not param_def:
            print(f"\n❌ {rule.parameter}: NO PARAMETER DEFINITION FOUND")
            continue
        
        # Get raw value
        field_ref = param_def.field_reference
        raw_value = lead.get(field_ref) if field_ref else None
        
        # Evaluate
        score = engine.evaluate_rule(rule, param_def, lead)
        
        print(f"\n📊 {rule.parameter}")
        print(f"   Field: {field_ref}")
        print(f"   Logic: {param_def.scoring_logic_type}")
        print(f"   Criteria: {rule.criteria}")
        print(f"   Raw Value: {raw_value} (type: {type(raw_value)})")
        print(f"   Score: {score} / {rule.max_score}")
    
    print("\n" + "=" * 80)
    print("FINAL REPORT:")
    print("=" * 80)
    
    # Generate full report
    total_possible = sum([float(d.max_score or 0) for d in template.details if d.active])
    report = engine.evaluate_lead(lead, total_possible)
    
    print(f"Total Score: {report['total_score']}")
    print(f"Category: {report['category']}")
    print(f"Section Scores: {report['section_scores']}")

test_test1122()
