# Tender Upgrade Progress Report (July 21, 2026)

This document consolidates our completed features, implementation plan, remaining task list, and walkthrough of all changes made to the custom Tender application so far.

---

## 1. Walkthrough of Changes Completed So Far

### Feature 1: Approx. Value in Words
- **Client-Side Event Listener**: Registered a handler on `approx_value_in_lakhs` in [tender.js](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.js) that translates the value (entered in lakhs) to words representing Indian Rupees.
- **Conversion Helper**: Added JS functions `num_to_words_indian` and `convert_whole_number` to format numeric currency to standard words (e.g. *Five Lakh Fifty Thousand Rupees Only* or *Paise*).
- **Dynamic Field Description**: Sets the description property dynamically on load and input change without dirtying the form state.

### Feature 2: Send-Back Date Setting (+1 Working Day, Skipping Sundays)
- **Workflow State Detection**: Inside `validate()` in [tender.py](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.py), we check if the transition is a send-back using the `_was_sent_back_to` helper.
- **Excluding Sundays**: Calculates target tab Work Initiation Date as `Send Back Date + 1 day`, using the custom `add_working_days(..., 1)` helper to skip Sundays. Target tab submission dates are successfully cleared.

### Feature 3: Forward Date Chaining (+1 Working Day, Skipping Sundays)
- **Python-Side Date Chaining**: Modified the date assignment inside `validate()` in [tender.py](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.py) so that each stage's Work Initiation Date defaults to the previous tab's submission date + 1 day (excluding Sundays).
- **JS-Side Synchronization**: Added `get_next_working_day` inside [tender.js](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.js) and updated all listeners/silent section calculators to keep client-side updates matching the server-side date chaining rule.

### Feature 4: Split Order Closure Form Structure (In Progress)
- **JSON Field Schema Updated**: Modified [tender.json](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.json) to:
  - Rename `tab_4_tab` label to `EVALUATION PROCESS`.
  - Add `section_break_eval_remarks`, `evaluation_remarks`, `column_break_eval_remarks`, and `evaluation_send_back_remarks` to the end of the **Evaluation Process** section.
  - Insert the new tab break `order_closure_tab` (label `ORDER CLOSURE`) right before the `order_approval_section` field.
  - Updated `field_order` list at the top of the schema file to place all fields in their correct tabs.

### Feature 5: Stage Auto-population & Full Section Coverage in Attachment Child Tables
- **Full Section Attachment Coverage**: Added attachment child tables (`vendor_evaluation_attachments`, `floating_enquiries_attachments`, `pre_bid_technical_meeting_attachments`, `introduction_meeting_attachments`, `mobilization_attachments`) across all sections in Evaluation Process and Vendor Onboarding in [tender.json](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.json).
- **Schema Updates**: Extended select options of the `stage` field in [tender_attachment.json](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender_attachment/tender_attachment.json) for all sections (`"vendor evaluation"`, `"floating enquiries"`, `"pre-bid / technical meeting"`, `"introduction meeting"`, `"mobilization"`, etc.).
- **Client-Side Event Handlers**: Registered parent table `_add` handlers and updated the child table listener mapping in [tender.js](file:///home/shalini/shaliniv15/apps/realapp/realapp/tender/doctype/tender/tender.js) to set the correct stage corresponding to each parent attachment field.

---

## 2. Implementation Plan for Workflow Split

### Required Workflow States
1. `Tender Creation` (Tab 1 editable, others hidden/read-only)
2. `Design Sample / Drawings` (Tab 2 editable, others hidden/read-only)
3. `BOQ Submission` (Tab 3 editable, others hidden/read-only)
4. `Evaluation Process` (Tab 4 editable, others hidden/read-only. Tab 5 hidden/read-only)
5. `Order Closure` (Tab 4 read-only, Tab 5 editable, others hidden/read-only)
6. `Vendor Finalisation` (Tab 6 editable, others hidden/read-only)
7. `Completed`

### Key Transition Rules
- **Submit BOQ**: Moves the state from `BOQ Submission` to `Evaluation Process` and sets `boq_submission_date` to today.
- **Submit Evaluation**: Moves the state from `Evaluation Process` to `Order Closure` and sets all Evaluation Process submission dates to today.
- **Submit Order Closure**: Moves the state from `Order Closure` to `Vendor Finalisation` and sets all Order Closure submission dates to today.
- **Send Back** (from `Evaluation Process`): Sends back to `BOQ Submission`. Uses `evaluation_send_back_remarks`.
- **Send Back** (from `Order Closure`): Sends back to `Evaluation Process`. Uses `order_closure_send_back_remarks`.

---

## 3. Tasks & Checklist (Remaining)

- [x] Modify `tender.json`
  - [x] Rename `tab_4_tab` label to "EVALUATION PROCESS"
  - [x] Insert new remarks section break and fields for Evaluation Process
  - [x] Insert `order_closure_tab` right before `order_approval_section`
  - [x] Update `field_order` list
- [x] Modify `tender.py`
  - [x] Update `state_order` dictionary mapping
  - [x] Update `revision_fields` dictionary mapping
  - [x] Update validate transition setting logic
  - [x] Update send-back date resetting logic
- [x] Modify `tender.js`
  - [x] Split tab fields into `tab4_fields` (Evaluation Process), `tab5_fields` (Order Closure), and `tab6_fields` (Vendor Onboarding)
  - [x] Update roles visibility check in `refresh(frm)`
  - [x] Update `before_workflow_action(frm)` transition settings
  - [x] Update send-back action handlers
- [/] Verify Changes
  - [ ] Verify files built and formatted correctly
  - [ ] Walkthrough the changes and write `walkthrough.md`
