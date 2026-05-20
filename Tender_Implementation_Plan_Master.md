# Master Implementation Plan: Tender Management Module

This document outlines the end-to-end architecture, completed features, and the roadmap for the Tender Management module, capturing the sequence of development across all phases.

---

## 🏁 Phase 1: Core Foundation (COMPLETED)

### [Tender Module Infrastructure]
- **Module Registration**: Created `Tender` module in `realapp`.
- **Naming Series**: Configured `TC-.####` naming series for work packages.
- **Tender Settings**: Single DocType for global cascading and threshold controls:
    - `enable_cascading`
    - `default_mode` (Manual, Suggestion, Auto)
    - `allow_override`, `require_approval_for_cascade`, `max_cascade_days`

### [Data Modeling]
- **Tender Calendar DocType**: Implemented the "Master Sheet" equivalent with:
    - Project context (Project, Type, Section).
    - Readiness (Sample Approval, Indigenous/Import).
    - **Lifecycle Stages**: BOQ → Pre-bid → Issue → Approval → Contract → Mobilization.
    - Financial & Execution tracking.

### [Reports & Dashboards]
- **Script Reports**:
    - `BOQ Status Report`
    - `Quotation Status Report`
    - `Order Status Report`
    - `Combined Tracker`
    - `Master Tender Calendar`
- **Dashboards**: Project Tender Dashboard and Procurement Tender Dashboard.

---

## 🔄 Phase 2: Intelligence & Cascading (COMPLETED)

### [Cascading Engine Controller Logic]
- **`tender_calendar.py` & `tender_calendar.js` Hooks**:
    - **Manual Mode**: No automated changes.
    - **Suggestion Mode**: Interactive UI prompt (`frappe.confirm`) to accept/reject date shifts when changes are made.
    - **Auto Mode**: Direct shift of downstream dates based on progressive delay ratios (BOQ → Tender Issue → Approval → Contract → Mobilization → Target Date).
    - **Impact Engine**: Automated `delay_days` and `impact_level` ("Low/Medium/High/Critical") labeling based on target date variance.

### [UI Enhancement - Unified Views]
- **Unified Calendar (`tender_calendar_calendar.js`)**: Custom JS view showing 5 events per record (color-coded).
- **Workspace (`tender.json`)**: Dedicated "Tender" hub with dashboards, quick links, and data tables.
- **Indicators**: Added "Indicators" to the DocType definition to show lifecycle health.

---

## 🚀 Phase 3: Sequence & Gantt Enhancements (COMPLETED)

### [Tender Calendar Schema (`tender_calendar.json`)]
- **`sl_no` Field**: Converted to `Int` type for native sorting.
- **`gantt_title` Field**: Added read-only background field to store descriptive titles (`Sequence - Category - Work Package`).

### [Sequence Recalculation Logic]
- **`before_insert` Hook**: Automatically calculate `sl_no` by finding the maximum for the current `project` and adding 1.
- **`validate` Hook**: Dynamically populate the `gantt_title` field.
- **`on_trash` Hook**: Recalculate sequence logic upon deletion to ensure gaps are closed and subsequent sequence numbers are shifted down.

### [Gantt View Configuration]
- **`tender_calendar_gantt.js`**: Updated the title mapping to use `gantt_title` so the sequence and category are visible in timeline views.

---

## 🏗️ Phase 4: Tower-Wise Custom Selection Engine (COMPLETED)

### [UI & Popups]
- **`tender_calendar.js` custom button**: Shows a checkbox checklist of remaining blocks when the project type is "Tower Wise".
- **Dynamic lists**: Fetches remaining blocks from the project that do not have generated lines.

### [Server Generation Logic]
- **`tender_calendar.py` functions**:
    - `get_remaining_blocks`: Returns blocks linked to the project excluding already generated ones.
    - `generate_selected_tower_tenders`: Programmatically clones the master template, binds the corresponding Block, appends the block suffix to the Work Package title, and generates new sequence numbers (`sl_no`).
    - **Deletion resilience**: If any block tender is deleted, the block becomes available again in the remaining blocks list of the Actions button.

---

## 🔒 Phase 5: Workflow Roles & Permissions Setup (COMPLETED)

### [Setup Scripts & Workspace Permissions]
- **`setup_permissions.py`**: Setup script to initialize workflow roles, custom permissions, and workspace access.
- **Workspace Access**: Configures role visibility for the `Tender Workspace` to support all 11 workflow roles.
- **Permissions Grid**: Planning roles and System Managers retain creation/deletion privileges; other roles receive edit-only permissions to collaborate on stage-gate updates.

### [Tender Calendar Workflow]
- **Workflow State Masters**: Pre-populates color badge styles in the database.
- **Tender Calendar Workflow**: A 14-state multi-role workflow from `Tender Creation` to `Completed`.
- **Transitions**: 26 transitions mapping step actions (e.g. `Send for Design`, `Submit Design`, `Submit BOQ`) to corresponding roles.
- **Verification & Deadlock Safeguards**:
  - Automated tests validating permission restrictions (`test_permission_restrictions`) and transitions (`test_workflow_transitions`).
  - Added deadlock safeguards by bypassing sequence shifting using `frappe.flags.skip_sequence_shift` during teardown/bulk operations.

---

## 🚦 Future Roadmap: Phase 6 & Beyond (PENDING)

### 🧩 Logic & Refinement
- **Cross-Tender Sequence Logic**: Expand on the sequence enhancements to build cross-record logic. Compare a work package's timeline against its immediate predecessor and color code delays to indicate dependency risks.
- **Stage-Gate Locking**: Enforce chronological validation rules at the workflow validation layer (e.g., Cannot transition past BOQ if BOQ date is not finalized).

### 🔔 Awareness & Integration
- **Notification Engine**: Daily email/Slack alerts for work packages nearing deadlines.
- **ERPNext Bridge**: Automatically creating RFQs in standard ERPNext from a Tender Calendar record.

---

## 🛠️ Global Verification Plan
1. **Reporting**: Verify that reports sort by `sl_no` ascending and exclude template records.
2. **Cascading**: Test "Suggestion Mode" and "Auto Mode" to ensure delay cascading behaves correctly.
3. **Sequencing**: Verify sequence auto-generation and gap-shifting logic works reliably on deletion.
4. **Tower Wise Generation**: Test block selection dialog and verify dynamic inclusion/exclusion.
5. **Workflow & Roles**: Run the automated test suite using `bench execute`:
   `bench --site selfcare.tridasa.in execute realapp.tender.doctype.tender_calendar.test_tender_calendar.run_tests`
