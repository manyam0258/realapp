import frappe
import math
from frappe.utils import today

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km using Haversine formula"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@frappe.whitelist()
def generate_lead_scoring_report(template_name):
    """Generates a new Lead Scoring Report based on the provided Template"""
    template = frappe.get_doc("Lead Scoring Template", template_name)
    project = frappe.get_doc("Project", template.project)
    leads = frappe.get_all("Lead", fields=["*"])
    if not leads:
        frappe.throw("No leads found for evaluation.")

    # Create the report
    report = frappe.new_doc("Lead Scoring Report")
    report.project = project.name
    report.lead_scoring_template = template.name
    report.report_date = today()

    for lead in leads:
        lead_doc = frappe._dict(lead)
        total_score = 0
        section_scores = {}

        for rule in template.details:
            if not rule.active:
                continue

            score = evaluate_parameter(lead_doc, project, rule)
            weighted_score = (score * rule.weightage) / 100
            section_scores[rule.parameter] = weighted_score
            total_score += weighted_score

        category = categorize(total_score)

        report.append("details", {
            "lead": lead_doc.name,
            "total_score": total_score,
            "score_category": category,
            "section_scores": frappe.as_json(section_scores),
            "remarks": f"Scored using template {template_name}"
        })

    report.total_leads = len(leads)
    report.insert(ignore_permissions=True)
    frappe.db.commit()

    return report.name

def evaluate_parameter(lead, project, rule):
    """Evaluate individual rule logic"""
    try:
        field_value = lead.get(rule.parameter)
        if rule.scoring_logic_type == "GeoDistance":
            distance = haversine(
                float(lead.get("lead_latitude") or 0),
                float(lead.get("lead_longitude") or 0),
                float(project.latitude or 0),
                float(project.longitude or 0)
            )
            return rule.max_score if distance <= project.target_radius_km else 0

        elif rule.scoring_logic_type == "Match":
            return rule.max_score if str(rule.criteria).lower() in str(field_value).lower() else 0

        elif rule.scoring_logic_type == "Range":
            if "-" in str(rule.criteria):
                min_v, max_v = map(float, rule.criteria.split("-"))
                val = float(field_value or 0)
                return rule.max_score if min_v <= val <= max_v else 0

        elif rule.scoring_logic_type == "Custom" and rule.expression:
            return eval_custom_expression(rule.expression, lead, project, rule)

        return 0

    except Exception as e:
        frappe.log_error(f"Error in parameter {rule.parameter}: {e}", "Lead Scoring Engine")
        return 0

def eval_custom_expression(expression, lead, project, rule):
    """Safely evaluate custom Python expressions"""
    context = {"lead": lead, "project": project, "math": math}
    try:
        return eval(expression, {}, context)
    except Exception as e:
        frappe.log_error(f"Expression Error: {e}", "Lead Scoring Engine")
        return 0

def categorize(score):
    """Convert numerical score to qualitative category"""
    if score >= 80:
        return "Hot"
    elif score >= 60:
        return "Warm"
    else:
        return "Cold"
