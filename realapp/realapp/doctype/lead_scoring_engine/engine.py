import frappe
import math
from frappe.utils import today

def haversine(lat1, lon1, lat2, lon2):
    """Distance in KM using Haversine formula"""
    R = 6371
    try:
        dlat = math.radians(float(lat2) - float(lat1))
        dlon = math.radians(float(lon2) - float(lon1))
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(dlon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    except Exception:
        return 9999  # default if invalid coordinates

@frappe.whitelist()
def generate_lead_scoring_report(template_name):
    """Generate report for all Leads using a specific template"""
    template = frappe.get_doc("Lead Scoring Template", template_name)
    project = frappe.get_doc("Project", template.project)

    leads = frappe.get_all("Lead", fields=["*"])
    if not leads:
        frappe.throw("No leads found to evaluate.")

    results = []
    for lead in leads:
        lead_doc = frappe._dict(lead)
        total_score, section_scores = compute_lead_score(lead_doc, project, template)
        category = categorize(total_score)

        # create new report record
        report = frappe.new_doc("Lead Scoring Report")
        report.project = project.name
        report.lead_scoring_template = template.name
        report.lead = lead_doc.name
        report.total_score = total_score
        report.category = category
        report.section_scores = frappe.as_json(section_scores)
        report.report_date = today()
        report.insert(ignore_permissions=True)
        results.append(report.name)

    frappe.db.commit()
    return f"{len(results)} reports generated successfully."

def compute_lead_score(lead, project, template):
    """Compute score per lead based on template rules"""
    total_score = 0.0
    section_scores = {}

    for rule in template.details:
        if not rule.active:
            continue

        score = evaluate_parameter(lead, project, rule)
        weighted_score = (float(score) * float(rule.weightage)) / 100.0
        section_scores[rule.parameter] = round(weighted_score, 2)
        total_score += weighted_score

    return round(total_score, 2), section_scores

def evaluate_parameter(lead, project, rule):
    """Evaluate rule and return raw score"""
    try:
        value = lead.get(rule.parameter)
        if rule.scoring_logic_type == "GeoDistance":
            distance = haversine(
                lead.get("lead_latitude") or 0,
                lead.get("lead_longitude") or 0,
                project.latitude or 0,
                project.longitude or 0,
            )
            return rule.max_score if distance <= (project.target_radius_km or 5) else 0

        elif rule.scoring_logic_type == "Match":
            return rule.max_score if str(rule.criteria).lower() in str(value).lower() else 0

        elif rule.scoring_logic_type == "Range":
            if "-" in str(rule.criteria):
                min_v, max_v = map(float, rule.criteria.split("-"))
                return rule.max_score if min_v <= float(value or 0) <= max_v else 0

        elif rule.scoring_logic_type == "Custom" and rule.expression:
            return eval_custom_expression(rule.expression, lead, project, rule)

        return 0
    except Exception as e:
        frappe.log_error(f"Error in rule {rule.parameter}: {e}", "Lead Scoring Engine")
        return 0

def eval_custom_expression(expression, lead, project, rule):
    """Safely evaluate rule expressions"""
    context = {"lead": lead, "project": project, "math": math}
    try:
        val = eval(expression, {}, context)
        return float(val)
    except Exception as e:
        frappe.log_error(f"Expression error in {rule.parameter}: {e}")
        return 0

def categorize(score):
    """Score to category"""
    if score >= 80:
        return "Hot"
    elif score >= 60:
        return "Warm"
    else:
        return "Cold"
