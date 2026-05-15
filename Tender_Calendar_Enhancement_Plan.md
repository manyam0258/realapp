# Implementation Plan: Tender Calendar Enhancements

Based on the requirements to enhance the `Tender Calendar` with sequence sorting, status badge configuration, and automated "Tower Wise" generation, here is the proposed implementation plan:

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

## 3. Tower Wise Generation Engine
When a user selects `project_type` = "Tower Wise", we want to allow them to fill in the dates once, and then click a button to explode that record into individual line items for all 7 Towers (Blocks) in the Project.

**Action Plan:**
- **Database Schema Changes**:
  - Add a `block` (Link -> Block) field to `Tender Calendar`.
  - Add an `is_template` (Check) field (hidden) to identify the master record that spawned the child records.
  - Add a `towers_generated` (Check) field (read-only) to track if the generation has already occurred.
- **Client Script (`tender_calendar.js`)**:
  - Add a custom button **"Generate Tower Tenders"**.
  - Make the button visible ONLY IF `project_type == 'Tower Wise'` AND `towers_generated == 0`.
- **Server Script (`tender_calendar.py`)**:
  - Create a `@frappe.whitelist()` method `generate_tower_tenders`.
  - The method will query the `Block` DocType for all records linked to the current `project` (e.g., Tower A, Tower B, etc.).
  - For each Block, it will dynamically create a new `Tender Calendar` record by copying all dates, categories, and readiness fields from the master.
  - It will append the block name to the Work Package (e.g., `Painting Works - Tower A`).
  - It will assign the specific `Block` link to the new record.
  - Once all 7 are created, it sets `towers_generated = 1` and `is_template = 1` on the master record.
- **Report Updates**:
  - Modify the existing script reports (BOQ Tracker, Combined Tracker, etc.) to simply filter out records where `is_template = 1`. 
  - Because the 7 generated records are just standard `Tender Calendar` records, **they will automatically appear in all your existing reports** and calendar views with their own sequence numbers (`sl_no`), allowing users to edit the dates for each tower individually!

---

> Please confirm if this approach aligns with your vision. If approved, I can begin executing Phase 1 (Sorting & Status Badges) or Phase 3 (The Generation Engine) immediately!
