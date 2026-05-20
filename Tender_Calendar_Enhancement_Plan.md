# Implementation Plan: Tender Calendar Enhancements

Based on the requirements to enhance the `Tender Calendar` with sequence sorting, status badge configuration, automated "Tower Wise" generation, and role-based workflows, here is the updated enhancement plan:

## 1. Sequence (`sl_no`) in List View & Sorting
Currently, the `sl_no` is present but not configured as the primary sort field or visible in the list view.

**Action Plan:**
- **DocType Update (`tender_calendar.json`)**: 
  - Enable `In List View` for the `sl_no` field.
  - Change the `sort_field` from `modified` to `sl_no`.
  - Change the `sort_order` from `DESC` to `ASC`.
- **Result**: Whenever users open the Tender Calendar list, records will automatically be sorted 1, 2, 3, etc., making the sequence clear at a glance.

## 2. Order Status as Key Document Status
Currently, Frappe uses the `status` field (Finalised / Not Finalised) as the default document badge. We want `order_status` (Pending / Issued / Cancelled) to be the prominent badge in the UI.

**Action Plan:**
- **List View Override (`tender_calendar_list.js`)**: 
  - Create this file to override the default `get_indicator` function. 
  - It will read the `order_status` field and return the appropriate text and color (e.g., Orange for Pending, Green for Issued, Red for Cancelled).
- **Form View Override (`tender_calendar.js`)**:
  - Add logic in the `refresh` event using `frm.page.set_indicator(frm.doc.order_status, color)` to explicitly set the top-left badge of the document form to reflect the `Order Status`.
- **Why this approach?**: This is the safest "Frappe-way" because it visually changes the badge without needing to rename the actual database fields, ensuring existing reports and data aren't broken.

## 3. Tower Wise Generation Engine (Block-Wise Selection Popup)
When a user selects `project_type` = "Tower Wise", we want to allow them to fill in dates once and click a button to generate line items block-by-block using an interactive popup instead of generating all blocks at once.

**Action Plan:**
- **Database Schema Changes**:
  - Add a `block` (Link -> Block) field to `Tender Calendar`.
  - Add an `is_template` (Check) field (hidden) to identify the master record that spawned the child records.
  - Add a `towers_generated` (Check) field (read-only) to track if the generation has already occurred.
- **Client Script (`tender_calendar.js`)**:
  - Add custom action button **"Generate Tower Tenders"** under the Actions button.
  - Make the button visible if `project_type == 'Tower Wise'` and the master record is saved.
  - Show a customized `frappe.ui.Dialog` with a checklist of remaining blocks linked to the project.
- **Server Script (`tender_calendar.py`)**:
  - Create a `@frappe.whitelist()` method `get_remaining_blocks` to return blocks linked to the project that do not have a corresponding child `Tender Calendar` record.
  - Create a `@frappe.whitelist()` method `generate_selected_tower_tenders` to copy all dates/details from the master template to new records for each selected block, updating the Work Package title (e.g., `Painting Works - Tower A`).
  - Automatically update `towers_generated = 1` only when all blocks have been generated.
  - Support deleted sub-item re-generation (if a block's child record is deleted, it reappears in the actions button remaining blocks list).

## 4. Multi-State Workflow & Role-Based Permissions
To govern stage-gate progression and enforce collaborative access, we need to implement role-based document access controls and a 14-state approval workflow.

**Action Plan:**
- **Role Setup & Custom DocPerms**:
  - Implement a setup script `setup_permissions.py` to create 11 required roles (`Planning`, `Planning Head`, `Planning Manager`, `Architect`, `Quantity Surveyor`, `Procurement Team`, `Contracts Team`, `Project Team`, `Tender Committee`, `Management`, `Project Head`).
  - Configure Custom DocPerms: Planning roles and System Managers get full write/create/delete access; other roles get read/write (edit-only) access to collaborate.
  - Configure roles visibility for the Tender Workspace so all users can access it.
- **Workflow Setup**:
  - Programmatically create and activate the `"Tender Calendar Workflow"` linked to `Tender Calendar` doctype.
  - Define 14 states with custom styled color badges and map editing capabilities to the corresponding owner role for each step.
  - Configure 26 transition actions aligning the lifecycle steps from `Tender Creation` to `Completed`.
- **Validation & Verification**:
  - Write automated verification tests verifying role creation, restriction rules, and sequential workflow transitions.
  - Add database deadlock prevention safeguards to bypass sequence updates during bulk cleanup.
