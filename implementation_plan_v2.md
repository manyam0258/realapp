# Implementation Plan - Tender Cascading Engine & UI Enhancements

This plan outlines the implementation of the Cascading Engine and UI/Experience improvements for the `Tender Calendar` system, as prioritized in the roadmap.

## User Review Required

> [!IMPORTANT]
> The cascading logic will default to a 1:1 day shift for downstream dates unless specific offsets are requested. We will implement the "Auto" and "Suggestion" modes as defined in the global settings.

## Proposed Changes

### Cascading Engine

#### [MODIFY] [tender_calendar.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.py)
- Implement `validate` and `on_update` hooks.
- Logic for **Auto Mode**:
    - Detect changes in key date fields.
    - Calculate deltas.
    - Update `delay_days`.
    - Recursively shift downstream dates based on the sequence: BOQ → Tender Issue → Approval → Contract → Mobilization → Target Date.
    - Compute `impact_level` based on the stage and length of delay.

#### [MODIFY] [tender_calendar.js](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.js)
- Implement **Suggestion Mode**:
    - When a date is changed, trigger a client-side prompt `frappe.confirm` or `frappe.msgprint` showing the calculated impact on future dates.
    - Allow users to "Apply Shift" or "Ignore".
- Implement real-time chronological validation (e.g., Warning if `contract_date` is before `approval_date`).

---

### UI & Experience

#### [NEW] [tender_calendar_calendar.js](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar_calendar.js)
- Configure a custom calendar view that represents a single Tender record as multiple events:
    - Pre-Bid (Blue)
    - Tender Issue (Orange)
    - Approval (Green)
    - Contract (Purple)
    - Mobilization (Red)

#### [NEW] [Tender Workspace](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/workspace/tender/tender.json)
- Create a dedicated module workspace.
- Include:
    - Quick Links: New Tender, BOQ Tracker, Master Calendar.
    - Dashboard: Link the previously created "Project Tender Dashboard".
    - Data Tables: Show "Critical Tenders" (High/Critical impact).

#### [MODIFY] [tender_calendar.json](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.json)
- Add "Indicators" to the DocType definition to show lifecycle health (Red for delays, Green for on-track).

---

## Open Questions

1. **Specific Offsets**: The MD example shows BOQ +5 delay resulting in Mobilization +15. Should I use a 1:1 shift or should I build a configuration table for these progressive delays?
2. **Weekend Handling**: Should the cascading logic skip weekends/holidays when shifting dates?

## Verification Plan

### Automated Tests
- Server-side test in `test_tender_calendar.py` ensuring Auto-cascade shifts dates correctly.

### Manual Verification
1. Open a Tender Calendar record and shift the `boq_submission_date`.
2. Verify that in Suggestion mode, a prompt appears.
3. Verify that in Auto mode, downstream dates shift upon saving.
4. Verify the new "Tender" Workspace is accessible from the sidebar.
