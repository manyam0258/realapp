# Master Implementation Plan: Tender Management Module

This document outlines the end-to-end architecture, completed features, and the roadmap for the Tender Management module, capturing the sequence of development across all phases.

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

## 🚦 Future Roadmap: Phase 4 & Beyond (PENDING)

### 🧩 Logic & Refinement
- **Cross-Tender Sequence Logic**: Expand on the sequence enhancements to build cross-record logic. Compare a work package's timeline against its immediate predecessor and color code delays to indicate dependency risks.
- **Stage-Gate Locking**: Enforce chronological rules (e.g., Cannot set "Issued" status if "BOQ Status" is not "Submitted").

### 🚦 Workflow & Security
- **Approval Lifecycle**: Implementation of a 3-step workflow (Project Lead → Procurement Manager → Finalized).
- **Audit Logging**: Specific version history tracking for date changes to monitor manual overrides.

### 🔔 Awareness & Integration
- **Notification Engine**: Daily e-mail/Slack alerts for work packages nearing deadlines.
- **ERPNext Bridge**: Auto-creating RFQs in standard ERPNext from a Tender Calendar record.

## 🛠️ Global Verification Plan
1. **Reporting**: Verify that reports update in real-time when a record is saved.
2. **Cascading**: Test "Suggestion Mode" by delaying a BOQ date on a test record and verifying prompts.
3. **Sequencing**: Create/Delete records and verify the sequence stays unbroken and the Gantt chart reflects the sequence number correctly.
