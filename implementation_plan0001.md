# Implementation Plan - Tender Module for Realapp

This plan outlines the steps to create a new "Tender" module within the `realapp` Frappe application, implementing the core components described in the `Tender_Calendar_knowledgebase.md`.

## User Review Required

> [!IMPORTANT]
> The implementation will follow a phased approach. Phase 1 focuses on DocTypes and basic Reports. Cascading logic and advanced notifications will be implemented in subsequent phases as per the strategy in the knowledge base.

## Proposed Changes

### Tender Module Infrastructure

#### [NEW] Module Def: Tender
Create a new `Module Def` record named "Tender" associated with the `realapp` app.

#### [MODIFY] [modules.txt](file:///home/demo/frappe-bench2/apps/realapp/realapp/modules.txt)
Add "Tender" to the modules list.

---

### DocTypes

#### [NEW] DocType: Tender Settings
A Single DocType for global tender configurations.
- `enable_cascading` (Check)
- `default_mode` (Select: Manual, Suggestion, Auto)
- `allow_override` (Check)
- `require_approval_for_cascade` (Check)
- `max_cascade_days` (Int)

#### [NEW] DocType: Tender Calendar
The primary DocType for capturing tender data.
- **Fields**:
    - `sl_no` (Data)
    - `project` (Link to `Project`)
    - `work_package` (Data)
    - `category` (Data)
    - `sub_category` (Data)
    - `project_type` (Select: Project, Tower Wise, Club House)
    - `status` (Select: Finalised, Not Finalised)
    - `design_sample_approval` (Date)
    - `indigenous_import` (Select: Indigenous, Import)
    - `min_vendors_required` (Int)
    - `boq_submission_date` (Date)
    - `boq_submitted_date` (Date)
    - `boq_status` (Select: Yet to Submit, Submitted, NA)
    - `pre_bid_date` (Date)
    - `tender_issue_date` (Date)
    - `approval_date` (Date)
    - `contract_date` (Date)
    - `mobilization_date` (Date)
    - `target_date` (Date)
    - `actual_work_start` (Date)
    - `no_of_days` (Int)
    - `structure_schedule` (Data)
    - `vendors_to_onboard` (Small Text)
    - `vendor_count` (Int)
    - `contract_value_lakhs` (Currency)
    - `order_status` (Select: Pending, Issued, Cancelled)
    - `remarks` (Small Text)
    - `delay_info` (Small Text)

---

### Reports

#### [NEW] Script Reports
Create basic Script Report skeletons for:
1. `BOQ Status Report`
2. `Quotation Status Report`
3. `Order Status Report`
4. `Combined Tracker`
5. `Master Tender Calendar`

---

### Dashboards

#### [NEW] Dashboards & Charts
Create `Dashboard` records:
1. `Project Tender Dashboard`
2. `Procurement Tender Dashboard`

---

## Open Questions

1. **Naming Series**: Should `Tender Calendar` use a naming series (e.g., `TC-.####`) or a specific field?
2. **Work Package/Category**: Should these be Link fields to new Master DocTypes or just Data fields for now? (The MD suggests they are part of a Master Sheet, which implies they might be masters).

## Verification Plan

### Automated Tests
- None planned for Phase 1 infrastructure setup.

### Manual Verification
1. Verify "Tender" module appears in the desk.
2. Verify `Tender Calendar` and `Tender Settings` can be accessed and records created.
3. Verify reports and dashboards are visible (even if empty).
