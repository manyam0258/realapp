import frappe
from realapp.realapp.doctype.lead_scoring_engine.engine import LeadScoringEngine

def validate_engine():
    print("Starting Lead Scoring Engine validation...")
    
    # 1. Create a temporary project
    proj_name = "Scoring Test Project"
    if frappe.db.exists("Project", proj_name):
        frappe.delete_doc("Project", proj_name, force=True)
        
    project = frappe.get_doc({
        "doctype": "Project",
        "project_name": proj_name,
        "latitude": 12.9716,
        "longitude": 77.5946
    }).insert(ignore_permissions=True)
    print(f"Created temporary project: {project.name}")

    # 2. Create temporary Lead Scoring Dimension
    dim_name = "Financial"
    if not frappe.db.exists("Lead Scoring Dimension", dim_name):
        frappe.get_doc({
            "doctype": "Lead Scoring Dimension",
            "dimension_name": dim_name
        }).insert(ignore_permissions=True)
    print(f"Created temporary dimension: {dim_name}")

    # 3. Create temporary lead scoring parameter
    param_name = "Scoring Test Parameter"
    if frappe.db.exists("Lead Scoring Parameter", param_name):
        frappe.delete_doc("Lead Scoring Parameter", param_name, force=True)
        
    parameter = frappe.get_doc({
        "doctype": "Lead Scoring Parameter",
        "parameter_name": param_name,
        "dimension": dim_name,
        "scoring_logic_type": "Range",
        "field_reference": "annual_income",
        "max_score": 10,
        "active": 1
    }).insert(ignore_permissions=True)
    print(f"Created temporary parameter: {parameter.name}")

    # 3. Create temporary template
    template_name = "Scoring Test Template"
    if frappe.db.exists("Lead Scoring Template", template_name):
        frappe.delete_doc("Lead Scoring Template", template_name, force=True)
        
    template = frappe.get_doc({
        "doctype": "Lead Scoring Template",
        "template_name": template_name,
        "project": project.name,
        "status": "Active",
        "details": [
            {
                "parameter": parameter.name,
                "weightage": 10,
                "max_score": 10,
                "criteria": "500000",
                "scoring_logic_type": "Range",
                "active": 1
            }
        ]
    }).insert(ignore_permissions=True)
    print(f"Created temporary template: {template.name}")

    # 4. Create temporary lead
    lead_name = "Scoring Test Lead"
    existing = frappe.db.get_value("Lead", {"lead_name": lead_name})
    if existing:
        frappe.delete_doc("Lead", existing, force=True)
        
    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": lead_name,
        "annual_income": 600000,
        "latitude": 12.9716,
        "longitude": 77.5946
    }).insert(ignore_permissions=True)
    print(f"Created temporary lead: {lead.name}")

    # 5. Execute engine evaluation
    print("Instantiating LeadScoringEngine...")
    engine = LeadScoringEngine(template.name)
    
    rule = template.details[0]
    param_def = engine.get_parameter_definition(rule.parameter)
    raw_val = lead.get(param_def.field_reference)
    print(f"DEBUG: lead.annual_income = {lead.annual_income}")
    print(f"DEBUG: raw_val = {raw_val}")
    print(f"DEBUG: param_def.field_reference = {param_def.field_reference}")
    print(f"DEBUG: rule.criteria = {rule.criteria}")
    print(f"DEBUG: param_def.scoring_logic_type = {param_def.scoring_logic_type}")
    print(f"DEBUG: rule.max_score = {rule.max_score} (type: {type(rule.max_score)})")
    print(f"DEBUG: rule.scoring_logic_type = {rule.scoring_logic_type} (type: {type(rule.scoring_logic_type)})")
    
    # Run evaluate_rule
    score = engine.evaluate_rule(rule, param_def, lead)
    print(f"DEBUG: evaluate_rule returned = {score}")
    
    total_possible = sum([float(d.max_score or 0) for d in template.details if d.active])
    
    print("Evaluating lead...")
    report = engine.evaluate_lead(lead, total_possible)
    
    print("=" * 40)
    print(f"Total Score: {report['total_score']} (Expected: 100.0)")
    print(f"Category: {report['category']} (Expected: Hot)")
    print("=" * 40)
    
    # Assert correct behavior
    assert report["total_score"] == 100.0, "Total score is not 100.0"
    assert report["category"] == "Hot", "Category is not Hot"
    
    # Clean up created docs safely by rolling back
    frappe.db.rollback()
    print("Database changes rolled back. Lead Scoring Engine validated successfully!")

