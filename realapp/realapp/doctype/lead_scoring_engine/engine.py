import frappe, math
from frappe.utils import today


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance (km) between two points using the Haversine formula."""
    try:
        R = 6371.0
        lat1, lon1, lat2, lon2 = map(float, [lat1 or 0, lon1 or 0, lat2 or 0, lon2 or 0])
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    except Exception:
        return 9999


@frappe.whitelist()
def generate_lead_scoring_report(template_name):
    """Compute scores for all Leads using a given Lead Scoring Template, normalized to 100."""
    template = frappe.get_doc("Lead Scoring Template", template_name)
    project = frappe.get_doc("Project", template.project)
    leads = frappe.get_all("Lead", fields=["*"])

    if not leads:
        frappe.throw("No leads found to evaluate.")

    created_reports = []
    param_cache = {}

    total_possible_score = sum([float(d.max_score or 0) for d in template.details if d.active])
    if not total_possible_score:
        frappe.throw("No active parameters with max_score found in this template.")

    for lead_data in leads:
        lead = frappe._dict(lead_data)
        total_raw_score = 0.0
        section_scores = {}

        for rule in template.details:
            if not rule.active:
                continue

            param_name = getattr(rule, "parameter", None)
            pdoc = None
            if param_name:
                if param_name in param_cache:
                    pdoc = param_cache[param_name]
                else:
                    try:
                        pdoc = frappe.get_doc("Lead Scoring Parameter", param_name)
                    except Exception:
                        pdoc = None
                    param_cache[param_name] = pdoc

            field_ref = getattr(rule, "field_reference", None) or (pdoc.field_reference if pdoc else None)
            raw_value = None
            if field_ref:
                raw_value = lead.get(field_ref)
            elif rule.parameter:
                raw_value = lead.get(rule.parameter)

            raw_score = evaluate_rule_value(raw_value, lead, project, rule, pdoc)
            total_raw_score += float(raw_score or 0)
            section_scores[rule.parameter or (pdoc.name if pdoc else "unknown")] = round(raw_score or 0, 2)

        # Normalize to 100 scale
        normalized_score = (total_raw_score / total_possible_score) * 100
        total_score = round(normalized_score, 2)
        category = categorize(total_score)

        report = frappe.new_doc("Lead Scoring Report")
        report.project = project.name
        report.lead_scoring_template = template.name
        report.lead = lead.name
        report.total_score = total_score
        report.category = category
        report.section_scores = frappe.as_json(section_scores)
        report.report_date = today()
        report.insert(ignore_permissions=True)
        created_reports.append(report.name)

    frappe.db.commit()
    return f"{len(created_reports)} lead scoring reports generated successfully (normalized to 100)."


def evaluate_rule_value(raw_value, lead, project, rule, pdoc):
    """Return a raw score (0…rule.max_score) with normalization for bools, rupees, project-linked ranges, and geo."""
    try:
        logic = getattr(rule, "scoring_logic_type", None) or (pdoc.scoring_logic_type if pdoc else None)
        criteria = (getattr(rule, "criteria", None) or (pdoc.criteria if pdoc else None) or "").strip()
        max_score = float(getattr(rule, "max_score", None) or (pdoc.max_score if pdoc else 0) or 0)

        # 🧩 Normalize boolean fields
        if isinstance(raw_value, bool):
            raw_value = "Yes" if raw_value else "No"
        elif str(raw_value).strip() in ["1", "0"]:
            raw_value = "Yes" if str(raw_value).strip() == "1" else "No"

        # 💰 Handle annual_income specifically (in Rupees)
        if rule.field_reference and "annual_income" in rule.field_reference:
            val = float(raw_value or 0)
            if 2_00_000 <= val <= 1_00_00_000:
                # Expecting rupees, so compare directly
                raw_value = val
                criteria = "2000000-10000000"  # 20L–100L
            else:
                raw_value = val / 100000.0

        # 📍 GeoDistance logic
        if logic == "GeoDistance":
            lead_lat = lead.get("lead_latitude") or lead.get("latitude")
            lead_lon = lead.get("lead_longitude") or lead.get("longitude")
            distance = haversine(lead_lat, lead_lon, project.latitude or 0, project.longitude or 0)
            radius = getattr(project, "target_radius_km", None) or (float(criteria) if criteria else 5)
            return max_score if distance <= radius else 0

        # 🔤 Match / Exact
        if logic in ["Match", "Exact"]:
            if raw_value is None:
                return 0
            return max_score if str(criteria).lower() in str(raw_value).lower() else 0

        # 🔎 Contains (comma-separated match)
        if logic == "Contains":
            if raw_value is None:
                return 0
            for c in str(criteria).split(","):
                if str(c).strip().lower() in str(raw_value).lower():
                    return max_score
            return 0

        # 🔢 Range logic
        if logic == "Range":
            if raw_value is None:
                return 0

            # Dynamic range cases
            val = float(raw_value or 0)

            # Age Range → use project preferred range
            if "age" in (rule.parameter or "").lower():
                min_age = getattr(project, "preferred_age_min", None)
                max_age = getattr(project, "preferred_age_max", None)
                if min_age is not None and max_age is not None:
                    return max_score if float(min_age) <= val <= float(max_age) else 0

            # For purchase timeline, last_contact_days, etc.
            if not criteria:
                return 0
            try:
                if "-" in criteria:
                    mn, mx = [float(x.strip()) for x in criteria.split("-", 1)]
                    return max_score if mn <= val <= mx else 0
                thr = float(criteria)
                return max_score if val >= thr else 0
            except Exception:
                return 0

        # 🧠 Custom Expression
        if logic == "Custom":
            expr = getattr(rule, "expression", None) or (pdoc.example_expression if pdoc else None) or ""
            context = {"lead": lead, "project": project, "float": float, "math": math}
            try:
                result = eval(expr, {}, context)
                try:
                    return float(result)
                except Exception:
                    return max_score if bool(result) else 0
            except Exception as e:
                frappe.log_error(f"Custom expression error in {rule.parameter}: {e}", "Lead Scoring Engine")
                return 0

        return 0

    except Exception as e:
        frappe.log_error(f"Error evaluating {getattr(rule, 'parameter', None)}: {e}", "Lead Scoring Engine")
        return 0


def categorize(score):
    """Convert normalized score → category label."""
    try:
        s = float(score or 0)
        if s >= 80:
            return "Hot"
        if s >= 60:
            return "Warm"
        return "Cold"
    except Exception:
        return "Cold"
