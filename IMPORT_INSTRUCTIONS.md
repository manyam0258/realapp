# Lead Scoring Template - Import Instructions

## Quick Start
1. Open `lead_scoring_template_import.csv` in Excel or Google Sheets
2. Fill in your data starting from row after the sample (keep the headers!)
3. Go to Frappe UI → Data Import Tool → Select "Lead Scoring Template"
4. Upload the CSV file

## Import Format Guide

### Parent Fields (Lead Scoring Template)
- **ID**: Leave blank for new templates
- **Template Name**: Unique name for your template (e.g., "Luxury Residential Template")
- **Project**: Project ID (e.g., "PROJ-0001")
- **Status**: Draft, Active, or Inactive
- **Remarks**: Optional notes

### Child Fields (Lead Scoring Parameters - Details table)
For each row after the parent, add parameter rows:

- **Details: Parameter**: Name from Lead Scoring Parameter master (e.g., "Location", "Annual Income")
- **Details: Dimension**: The dimension category (auto-filled from Parameter, but you can override)
- **Details: Scoring Logic Type**: One of:
  - `GeoDistance` - For location-based scoring
  - `Match` - For exact value match
  - `Contains` - For checking if value exists in comma-separated list
  - `Range` - For numeric ranges (format: "min-max" or single threshold)
  - `Custom` - For Python expressions
  
- **Details: Criteria**: 
  - For `GeoDistance`: Radius in km (e.g., "10")
  - For `Match`: Exact value to match (e.g., "Married", "1")
  - For `Contains`: Comma-separated list (e.g., "IT, Business Owner")
  - For `Range`: "min-max" format (e.g., "30-50", "2000000-10000000")
  - For `Custom`: Leave blank (use Expression column)
  
- **Details: Weightage**: Percentage weight (sum should be ~100%)
- **Details: Max Score**: Maximum points for this parameter
- **Details: Custom Expression (Optional)**: Python code for Custom logic type
  - Example: `lead.annual_income >= project.avg_unit_price * 0.25`
  - Available: `lead`, `project`, `math`, `flt`, `cint`

## Important Logic Type Rules

### ❌ Common Mistakes
1. **GeoDistance with city name**: Use numeric radius only
   - ❌ Wrong: `Criteria = "Hyderabad"`
   - ✅ Correct: `Criteria = "10"` (10 km radius)

2. **Match with Python code**: Use Custom instead
   - ❌ Wrong: `Logic=Match, Criteria="lead.age > 30"`
   - ✅ Correct: `Logic=Custom, Expression="lead.age > 30"`

3. **Match with range**: Use Range instead
   - ❌ Wrong: `Logic=Match, Criteria="30-50"`
   - ✅ Correct: `Logic=Range, Criteria="30-50"`

4. **Contains for list check**: Perfect for multi-select
   - ✅ Correct: `Logic=Contains, Criteria="IT, Business Owner, NRI"`

### ✅ Correct Examples by Logic Type

**GeoDistance:**
```
Logic: GeoDistance
Criteria: 10
```

**Match:**
```
Logic: Match
Criteria: Married
```

**Contains:**
```
Logic: Contains  
Criteria: IT, Business Owner, NRI
```

**Range:**
```
Logic: Range
Criteria: 30-50
```

**Custom:**
```
Logic: Custom
Criteria: (ignored)
Expression: lead.decision_maker_type in ['Self', 'Spouse']
```

## Tips
- Keep one template per row for the parent
- Add multiple parameter rows below with same template columns blank (Excel will merge)
- Total weightage should add up to 100%
- Verify parameter names exist in "Lead Scoring Parameter" master first
