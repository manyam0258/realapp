import frappe
import math
from frappe.utils import today, flt, cint

class LeadScoringEngine:
    def __init__(self, template_name):
        self.template_name = template_name
        self.template = frappe.get_doc("Lead Scoring Template", template_name)
        self.project = frappe.get_doc("Project", self.template.project)
        self.param_cache = {}
        self.reports_created = 0

    def generate_reports(self, batch_size=1000):
        """
        Generates lead scoring reports for all leads in batches.
        """
        # Get total count of leads for progress tracking (optional)
        total_leads = frappe.db.count("Lead")
        
        # Process in batches
        for start in range(0, total_leads, batch_size):
            leads = frappe.get_all("Lead", fields=["*"], limit_start=start, limit_page_length=batch_size)
            if not leads:
                break
            
            self.process_batch(leads)
            frappe.db.commit() # Commit after each batch to avoid large transaction logs

        return f"{self.reports_created} lead scoring reports generated successfully."

    def process_batch(self, leads):
        """
        Processes a batch of leads and inserts reports.
        """
        reports_to_insert = []
        
        # Pre-calculate total possible score from active rules
        total_possible_score = sum([flt(d.max_score or 0) for d in self.template.details if d.active])
        if not total_possible_score:
            frappe.log_error("Lead Scoring Template has no active parameters with max_score", self.template_name)
            return

        for lead_data in leads:
            lead = frappe._dict(lead_data)
            
            # Evaluate Lead
            report_data = self.evaluate_lead(lead, total_possible_score)
            
            # Check if report already exists for this lead and template to avoid duplicates
            # For performance in bulk, we might skip this check or do a bulk delete first.
            # Here, let's delete existing report for this lead/template combination to ensure idempotency.
            frappe.db.delete("Lead Scoring Report", {
                "lead": lead.name,
                "lead_scoring_template": self.template.name
            })

            # Create new report doc (not inserted yet)
            report = frappe.new_doc("Lead Scoring Report")
            report.update(report_data)
            report.insert(ignore_permissions=True)
            self.reports_created += 1

    def evaluate_lead(self, lead, total_possible_score):
        """
        Evaluates a single lead against the template rules.
        """
        total_raw_score = 0.0
        section_scores = {}

        for rule in self.template.details:
            if not rule.active:
                continue

            # Get Parameter definition (cached)
            param_def = self.get_parameter_definition(rule.parameter)
            if not param_def:
                continue

            # Determine Score
            raw_score = self.evaluate_rule(rule, param_def, lead)
            total_raw_score += flt(raw_score)
            
            # Track section scores
            key = rule.parameter
            section_scores[key] = round(raw_score, 2)

        # Normalize Score
        normalized_score = (total_raw_score / total_possible_score) * 100 if total_possible_score else 0
        total_score = round(normalized_score, 2)
        category = self.categorize_score(total_score)

        return {
            "project": self.project.name,
            "lead_scoring_template": self.template.name,
            "lead": lead.name,
            "total_score": total_score,
            "category": category,
            "section_scores": frappe.as_json(section_scores),
            "report_date": today()
        }

    def get_parameter_definition(self, param_name):
        if param_name not in self.param_cache:
            try:
                self.param_cache[param_name] = frappe.get_doc("Lead Scoring Parameter", param_name)
            except Exception:
                self.param_cache[param_name] = None
        return self.param_cache[param_name]

    def evaluate_rule(self, rule, param_def, lead):
        """
        Evaluates a specific rule for a lead.
        Logic type is derived from the Parameter definition.
        """
        try:
            # 1. Identify Logic Type & Configuration
            # CRITICAL FIX: Template Detail can override Parameter logic type
            # This allows users to use different logic in different templates for the same parameter
            # Priority: Template Detail > Parameter Definition
            logic_type = rule.scoring_logic_type or param_def.scoring_logic_type
            
            # Criteria: Template overrides Parameter
            criteria = (rule.criteria or param_def.criteria or "").strip()
            
            # Max Score comes from Template Rule (as per user request: "user will only update the scoring and weightage")
            max_score = flt(rule.max_score)

            # Field Reference comes from Parameter
            field_ref = param_def.field_reference
            
            # Get Raw Value from Lead
            raw_value = lead.get(field_ref) if field_ref else None

            # 2. Evaluate based on Logic Type
            if logic_type == "GeoDistance":
                return self.evaluate_geodistance(lead, criteria, max_score)
            
            elif logic_type == "Match" or logic_type == "Exact":
                return self.evaluate_match(raw_value, criteria, max_score)
            
            elif logic_type == "Contains":
                return self.evaluate_contains(raw_value, criteria, max_score)
            
            elif logic_type == "Range":
                return self.evaluate_range(raw_value, criteria, max_score)
            
            elif logic_type == "Custom":
                return self.evaluate_custom(rule, param_def, lead, max_score)
            
            return 0.0

        except Exception as e:
            frappe.log_error(f"Error evaluating rule {rule.parameter}: {e}", "Lead Scoring Engine")
            return 0.0

    def evaluate_geodistance(self, lead, criteria, max_score):
        # Get Lead Coordinates
        lead_lat = flt(lead.get("lead_latitude") or lead.get("latitude") or 0)
        lead_lon = flt(lead.get("lead_longitude") or lead.get("longitude") or 0)
        
        # Get Project Coordinates
        proj_lat = flt(self.project.latitude or 0)
        proj_lon = flt(self.project.longitude or 0)

        if not (lead_lat and lead_lon and proj_lat and proj_lon):
            return 0.0

        distance = self.haversine(lead_lat, lead_lon, proj_lat, proj_lon)
        
        # Criteria is the radius in km
        radius = flt(criteria) if criteria else 5.0 # Default 5km if not specified
        
        if distance <= radius:
            return max_score
        return 0.0

    def evaluate_match(self, raw_value, criteria, max_score):
        if raw_value is None:
            return 0.0
        
        # Normalize booleans
        val_str = str(raw_value).lower().strip()
        if isinstance(raw_value, bool) or val_str in ["1", "0", "true", "false"]:
             if val_str in ["1", "true"]: val_str = "yes"
             elif val_str in ["0", "false"]: val_str = "no"
        
        crit_str = str(criteria).lower().strip()
        
        if val_str == crit_str:
            return max_score
        return 0.0

    def evaluate_contains(self, raw_value, criteria, max_score):
        if raw_value is None:
            return 0.0
        
        val_str = str(raw_value).lower()
        # Criteria is comma-separated list
        options = [x.strip().lower() for x in str(criteria).split(",")]
        
        for opt in options:
            if opt and opt in val_str:
                return max_score
        return 0.0

    def evaluate_range(self, raw_value, criteria, max_score):
        if raw_value is None:
            return 0.0
        
        val = flt(raw_value)
        
        # Criteria formats: "min-max" or "threshold" (assumed >= threshold)
        try:
            if "-" in str(criteria):
                parts = str(criteria).split("-")
                if len(parts) == 2:
                    mn = flt(parts[0])
                    mx = flt(parts[1])
                    if mn <= val <= mx:
                        return max_score
            else:
                # If single value, assume it's a minimum threshold? 
                # Or exact match? Range usually implies comparison.
                # Let's assume >= threshold if single number provided for Range type
                threshold = flt(criteria)
                if val >= threshold:
                    return max_score
        except Exception:
            pass
            
        return 0.0

    def evaluate_custom(self, rule, param_def, lead, max_score):
        # Expression comes from Parameter (example_expression) or Rule (expression)
        # User said "template will pull config from parameter", but Template Detail has an 'expression' field too.
        # We'll check Rule first, then Parameter.
        expr = rule.expression or param_def.example_expression
        if not expr:
            return 0.0
            
        context = {
            "lead": lead,
            "project": self.project,
            "math": math,
            "flt": flt,
            "cint": cint,
            "frappe": frappe
        }
        
        try:
            result = eval(expr, {"__builtins__": {}}, context)
            # If result is boolean, return max_score or 0
            if isinstance(result, bool):
                return max_score if result else 0.0
            # If result is number, return it (capped at max_score?)
            # Usually custom logic returns a score directly or a multiplier.
            # Let's assume it returns the score to be used.
            return flt(result)
        except Exception as e:
            frappe.log_error(f"Custom expression error: {e}", "Lead Scoring Engine")
            return 0.0

    def categorize_score(self, score):
        if score >= 80:
            return "Hot"
        if score >= 60:
            return "Warm"
        return "Cold"

    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        """Calculate distance (km) between two points using the Haversine formula."""
        try:
            R = 6371.0
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c
        except Exception:
            return 9999.0

@frappe.whitelist()
def generate_lead_scoring_report(template_name):
    engine = LeadScoringEngine(template_name)
    return engine.generate_reports()
