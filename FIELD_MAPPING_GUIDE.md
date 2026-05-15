# Lead Scoring - Definitive Field Mapping Guide

## Quick Reference Table

| Parameter Name | Lead Field | Field Type | Best Logic Type | Criteria Format | Example Criteria | Notes |
|---|---|---|---|---|---|
| **Location** | `lead_latitude`, `lead_longitude` | decimal | **GeoDistance** | Radius in km | `10` | Requires project lat/lon |
| **Employment Type** | `employment_type` | varchar | **Contains** | Comma-separated | `IT, Business Owner, NRI` | Use Contains for multi-select |
| **Marital Status** | `marital_status` | varchar | **Match** | Exact string | `Married` | Case-sensitive |
| **Age Range** | `lead_age` | int | **Range** | min-max | `30-50` | Numeric range |
| **Annual Income** | `annual_income` | decimal | **Range** | min-max | `2000000-10000000` | In rupees |
| **Budget Fit** | `annual_income` | decimal | **Custom** | (ignored) | Expression: `lead.annual_income >= project.avg_unit_price * 0.25` | Complex logic |
| **Loan Pre-approved** | `loan_preapproved` | tinyint (0/1) | **Match** | Boolean value | `1` | 1=Yes, 0=No |
| **Existing Property Owner** | `existing_property_owner` | tinyint (0/1) | **Match** | Boolean value | `1` | 1=Yes, 0=No |
| **Has Kids** | `has_kids` | tinyint (0/1) | **Match** | Boolean value | `1` | 1=Yes, 0=No |
| **Site Visit Scheduled** | `site_visit_scheduled` | tinyint (0/1) | **Match** | Boolean value | `1` | 1=Yes, 0=No |
| **Last Contact Days** | `last_contact_days` | int | **Range** | min-max or threshold | `0-7` | Days since last contact |
| **Purchase Timeline** | `purchase_timeline` | int | **Range** | min-max | `0-3` | Months to purchase |
| **Decision Maker Type** | `decision_maker_type` | varchar | **Contains** or **Custom** | List or Expression | `Self, Spouse` OR Expression: `lead.decision_maker_type in ['Self', 'Spouse']` | Use Contains for simple lists |
| **Urgency Reason** | `urgency_reason` | varchar | **Contains** | Comma-separated | `job relocation, lease expiry, investment` | Case-insensitive matching |

## Logic Type Decision Tree

```
START: What type of data are you scoring?
│
├─ Geographic coordinates (lat/lon)?
│  └─ Use: GeoDistance
│     Criteria: Radius in km (e.g., "10")
│
├─ Boolean field (Yes/No, 0/1)?
│  └─ Use: Match
│     Criteria: "1" for Yes, "0" for No
│
├─ Numeric field (age, income, days)?
│  ├─ Simple range check (min-max)?
│  │  └─ Use: Range
│  │     Criteria: "min-max" (e.g., "30-50", "2000000-10000000")
│  │
│  └─ Complex calculation (comparing to project fields)?
│     └─ Use: Custom
│        Expression: Python code (e.g., "lead.annual_income >= project.avg_unit_price * 0.25")
│
├─ Text field (employment, city, reason)?
│  ├─ Check if value is in a list of options?
│  │  └─ Use: Contains
│  │     Criteria: Comma-separated list (e.g., "IT, Business Owner, NRI")
│  │
│  ├─ Exact match to one value?
│  │  └─ Use: Match
│  │     Criteria: Exact string (e.g., "Married")
│  │
│  └─ Complex text logic (multiple conditions)?
│     └─ Use: Custom
│        Expression: Python code (e.g., "lead.urgency_reason.lower() in ['job relocation', 'investment']")
│
└─ Complex logic across multiple fields?
   └─ Use: Custom
      Expression: Python code with access to lead, project, math, flt, cint
```

## Common Mistakes & Solutions

### ❌ Mistake 1: Using Match for Boolean fields with "Yes"/"No"
```
Wrong:  Logic=Match, Criteria="Yes"
Correct: Logic=Match, Criteria="1"
```
**Why**: Database stores boolean as 0/1, not "Yes"/"No"

### ❌ Mistake 2: Using Match for lists
```
Wrong:  Logic=Match, Criteria="IT, Business Owner"
Correct: Logic=Contains, Criteria="IT, Business Owner"
```
**Why**: Match requires exact match of entire string

### ❌ Mistake 3: Using Match for ranges
```
Wrong:  Logic=Match, Criteria="30-50"
Correct: Logic=Range, Criteria="30-50"
```
**Why**: Match looks for the exact string "30-50", not a range

### ❌ Mistake 4: Using GeoDistance with city name
```
Wrong:  Logic=GeoDistance, Criteria="Hyderabad"
Correct: Logic=GeoDistance, Criteria="10"
```
**Why**: GeoDistance expects numeric radius in km

### ❌ Mistake 5: Putting Python code in Criteria for Match logic
```
Wrong:  Logic=Match, Criteria="lead.age > 30"
Correct: Logic=Custom, Expression="lead.age > 30"
```
**Why**: Match compares values, Custom evaluates code

### ❌ Mistake 6: Case-sensitive text matching
```
Wrong:  Logic=Contains, Criteria="Investment" (lead has "investment")
Correct: Logic=Contains, Criteria="investment" OR use Custom with .lower()
```
**Why**: Contains is case-sensitive by default in our engine

## Field Type Reference

### Boolean Fields (tinyint)
- **Database Value**: 0 or 1
- **Display Value**: Unchecked or Checked
- **For Scoring**: Use `Criteria="1"` to match checked

**Examples**:
- `loan_preapproved`
- `existing_property_owner`
- `has_kids`
- `site_visit_scheduled`

### Numeric Fields (int, decimal)
- **Range Check**: Use Range logic with "min-max"
- **Threshold Check**: Use Range logic with single number (>=)
- **Complex Math**: Use Custom with expressions

**Examples**:
- `lead_age` (int)
- `annual_income` (decimal)
- `last_contact_days` (int)
- `purchase_timeline` (int)

### Text Fields (varchar)
- **Exact Match**: Use Match
- **List Check**: Use Contains
- **Complex Text**: Use Custom

**Examples**:
- `employment_type`
- `marital_status`
- `decision_maker_type`
- `urgency_reason`

## Custom Expression Examples

### Example 1: Budget Check
```python
lead.annual_income >= project.avg_unit_price * 0.25
```
Returns: Boolean (True/False) → Converted to max_score or 0

### Example 2: Multiple Field Check
```python
lead.decision_maker_type in ['Self', 'Spouse'] and lead.marital_status == 'Married'
```

### Example 3: Text Contains (Case-insensitive)
```python
lead.urgency_reason and lead.urgency_reason.lower() in ['job relocation', 'lease expiry', 'investment']
```

### Example 4: Numeric Calculation
```python
(lead.annual_income / 12) * 0.4  # Returns EMI capacity
```
Returns: Number → Used directly as score (capped at max_score if needed)

## Best Practices

1. **Use the Simplest Logic Type That Works**
   - Don't use Custom if Match/Range/Contains will do
   - Custom expressions are harder to debug

2. **Be Consistent with Case**
   - Store data in lowercase or use `.lower()` in expressions
   - Document your case conventions

3. **Validate Field Names**
   - Always check `field_reference` exists in Lead doctype
   - Use `bench console` to verify: `frappe.get_meta("Lead").get_field("field_name")`

4. **Test with Real Data**
   - Check actual values: `frappe.db.get_value("Lead", "CRM-LEAD-2025-00001", "field_name")`
   - Verify data types match your logic

5. **Document Complex Logic**
   - Add comments in Custom expressions
   - Use Template Remarks field to explain scoring strategy

## Debugging Checklist

When a parameter returns 0:

- [ ] Check `field_reference` is correct
- [ ] Verify Lead has data in that field
- [ ] Confirm data type matches logic type
- [ ] Test Criteria format (e.g., "1" not "Yes" for boolean)
- [ ] For Custom: Check Expression syntax
- [ ] For Range: Verify numeric format ("min-max" not "min to max")
- [ ] For Contains: Check case sensitivity
- [ ] For GeoDistance: Verify lat/lon exist and are non-zero

## Testing Commands

```python
# Check Lead data
bench --site demooo console
lead = frappe.get_doc("Lead", "CRM-LEAD-2025-00001")
print(lead.employment_type)  # Check actual value
print(type(lead.has_kids))   # Check data type

# Test engine manually
from realapp.realapp.doctype.lead_scoring_engine.engine import LeadScoringEngine
engine = LeadScoringEngine("Test1122")
result = engine.evaluate_lead(lead, 100)
print(result)
```
