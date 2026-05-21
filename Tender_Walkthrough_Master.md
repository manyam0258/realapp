# Walkthrough

## Changes Made

### 1. Date Formatting Fix (Previous Phase)
- **Report**: [master_tender_calendar.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/report/master_tender_calendar/master_tender_calendar.py)
- Replaced database-specific `DATE_FORMAT(target_date, '%%M %%Y')` with python formatting `strftime("%B %Y")`.
- This resolves database-specific parsing issues where the month was displayed literally as `%M %Y`.

### 2. Workflow Stage Integration & 'Send Back' Transitions (Current Phase)
- **Workflow Fixtures & Setup**:
  - Updated [workflow.json](file:///home/demo/frappe-bench2/apps/realapp/realapp/fixtures/workflow.json) and [setup_permissions.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/setup_permissions.py) to add the new `"Send Back"` transitions:
    - **BOQ Submission** $\rightarrow$ **Design Sample / Drawings** (Planning, QS)
    - **Technical Evaluation** $\rightarrow$ **Vendor Finalisation** (Project Team, Procurement, Management)
    - **Order for Approval** $\rightarrow$ **Supplier Negotiation - 2** (Tender Committee, Management)
    - **Contract Agreement / Issue of Order** $\rightarrow$ **Order for Approval** (Procurement, Contracts)
  - Registered `"Send Back"` in the `Workflow Action Master` filters list in [hooks.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/hooks.py) for clean fixture export.

- **Validation Rules**:
  - Added client-side validation in [tender_calendar.js](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.js) inside the `before_workflow_action(frm)` event to:
    1. Check if the form is dirty (`frm.is_dirty()`). If dirty when triggering a `"Send Back"` transition, unfreeze the UI, block the transition, and prompt the user to save changes first.
    2. Check if the `remarks` field is empty during a `"Send Back"` transition (only if form is not dirty/saved). If empty, set the field as required (`frm.toggle_reqd("remarks", true)`), scroll to the field (`frm.scroll_to_field("remarks")`), focus on the input, show a validation warning, and reject the transition.
    3. Explicitly clear the `remarks` field client-side (`frm.set_value("remarks", "")`) when executing any forward/non-Send-Back transition.
  - Resolved a UI freeze issue where rejecting the workflow action left the screen greyed out due to Frappe's synchronous overlay locking: introduced a deferred `frappe.dom.unfreeze()` call via `setTimeout` to ensure the `#freeze` backdrop is cleanly removed from the DOM after the event loop tick.
  - Added matching server-side validation in [tender_calendar.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.py) (`validate_workflow_send_back`) to block API-level updates if `remarks` is empty on a send-back transition.

- **UI & Views Updates**:
  - Removed custom page badge / status indicators from [tender_calendar.js](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.js) to prevent duplicate/overlapping status indicators on form load.
  - Updated list view in [tender_calendar_list.js](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar_list.js) to display indicators based on the `workflow_state` instead of the static `order_status` field.

- **Reports Update**:
  - Modified [master_tender_calendar.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/report/master_tender_calendar/master_tender_calendar.py) and [order_status_report.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/report/order_status_report/order_status_report.py) to replace the "Order Status" column with "Workflow State", retrieving and rendering the actual active workflow stage of the line item.

- **Layout Reorganization**:
  - Added 9 new `Column Break` fields to [tender_calendar.json](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.json) and inserted them into the `field_order` list.
  - This configures 2-column layouts for all 11 existing sections to make the document page significantly more compact, organized, and readable.

---

## Verification Results

### Automated Verification
1. Ran `bench execute` on both report modules. The commands returned successfully showing rows with active workflow stages (e.g. `"workflow_state": "Tender Creation"`) instead of legacy status strings:
   ```bash
   bench --site selfcare.tridasa.in execute realapp.tender.report.master_tender_calendar.master_tender_calendar.execute
   bench --site selfcare.tridasa.in execute realapp.tender.report.order_status_report.order_status_report.execute
   ```
2. Ran a programmatic validation script. When trying to transition to a prior state without remarks, the validator successfully intercepted the request and threw `ValidationError: Remarks are mandatory when sending back the workflow.` When remarks were supplied, the transition completed successfully.
3. Ran `bench migrate` to sync the updated DocType schema layout (including the new column breaks) with the database. The migration completed successfully.
