# Tender Calendar DocType Layout Reorganization

This plan describes how we will rearrange the fields of the `Tender Calendar` DocType. We will keep all 11 existing sections exactly as they are, but introduce `Column Break` fields within each section so that the fields are organized in two columns. This will significantly decrease the vertical page scroll length of the form.

## User Review Required

> [!IMPORTANT]
> We will add 8 new `Column Break` fields to divide the following sections into 2-columns:
> 1. **Top Section**:
>    - Left: `sl_no`, `project`, `block`, `work_package`
>    - Right: `category`, `sub_category`
> 2. **Project Context**:
>    - Left: `project_type`
>    - Right: `status`
> 3. **Procurement Readiness**:
>    - Left: `design_sample_approval`
>    - Right: `indigenous_import`, `min_vendors_required`
> 4. **BOQ Tracking**:
>    - Left: `boq_submission_date`
>    - Right: `boq_submitted_date`, `boq_status`
> 5. **Tender Lifecycle**:
>    - Left: `pre_bid_date`, `tender_issue_date`, `approval_date`
>    - Right: `contract_date`, `mobilization_date`
> 6. **Execution**:
>    - Left: `target_date`, `actual_work_start`
>    - Right: `no_of_days`
> 7. **Vendor Tracking**:
>    - Left: `vendors_to_onboard`
>    - Right: `vendor_count`, `order_type`
> 8. **Status & Remarks**:
>    - Left: `order_status`, `remarks`
>    - Right: `delay_info`
> 9. **System Controls**:
>    - Left: `cascading_mode`, `delay_days`, `impact_level`
>    - Right: `naming_series`, `is_template`, `towers_generated`
>
> Sections with a single field (like **Construction Link** and **Financial**) will remain full-width.

## Open Questions

None at this time.

---

## Proposed Changes

### DocType Schema Configuration

#### [MODIFY] [tender_calendar.json](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.json)
- Modify the `field_order` list to insert the 8 new Column Breaks.
- Add definition blocks for the 8 new Column Break fields in the `fields` array:
  - `column_break_header`
  - `column_break_project_context`
  - `column_break_readiness`
  - `column_break_boq`
  - `column_break_lifecycle`
  - `column_break_execution`
  - `column_break_vendor`
  - `column_break_remarks`
  - `column_break_system`

---

## Verification Plan

### Automated Verification
- Run `bench migrate` to sync the new DocType structure to the database.
- Verify that `bench migrate` completes with no errors.

### Manual Verification
- Open a `Tender Calendar` document in the desk view and check that fields are properly aligned into two columns per section, and the page is much shorter and more readable.
