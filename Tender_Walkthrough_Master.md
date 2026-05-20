# Master Walkthrough: Tender Management Module

Welcome to the Tender Management module. This module provides a robust, data-driven engine for procurement planning and execution. This walkthrough demonstrates the sequence of features developed and outlines the path forward.

---

## 🌟 Phase 1: Core Foundation & Unified Tender Hub

### 1. The Unified Tender Hub
- **Tender Workspace**: A central dashboard for procurement managers.
- **Milestone Indicators**: Projects and work packages are color-coded in the list view (e.g., Red for "Critical" impact tenders).

### 2. Unified Visualizations
- **The Lifecycle Calendar**: 
    - Showing **5 distinct events** for every single tender record (Pre-Bid, Issue, Approval, Contract, Mobilization).
    - Color-coded by event type for easy multi-track management.
- **Procurement Gantt**: Standard timeline view from BOQ start to project handover.

### 3. Advanced Business Intelligence (5 Reports)
- **BOQ Tracker**: Monitors "Planned vs Actual" and highlights "Yet to Submit" items.
- **Quotation Coverage**: Tracks if enough vendors have been onboarded vs the requirement.
- **Financial Status**: Summarizes contract values (Lakhs) and order issuance progress.
- **Combined Master Sheet**: A flat, horizontal view of the entire procurement pipeline.
- **Monthly Pipeline**: A chart-driven report showing work package targets by month.

---

## 🔄 Phase 2: Cascading Engine & UI Enhancements

### 1. Date Management (Cascading Engine)
- **Auto Mode**: Automatically shifts downstream dates when the `BOQ Submission Date` is delayed. It follows a progressive buffer logic:
    - Tender Issue: +D
    - Approval: +D+2
    - Contract: +D+5
    - Mobilization/Target: +D+10
- **Suggestion Mode**: Detects date changes in the browser and prompts the user to apply the calculated shift across the lifecycle.
- **Manual Mode**: Allows independent date management without automatic shifting.

### 2. Validation & Impact Engine
- **Impact Engine**: Calculates `delay_days` and `impact_level` (Low, Medium, High, Critical) automatically on save based on the `Target Date`.
- **Chronological Guardrails**: Real-time warnings if dates are entered out of sequence (e.g., Contract before Approval).

---

## 🚀 Phase 3: Sequence & Gantt Enhancements

### 1. Robust Sequence Auto-Generation
The `sl_no` (Serial Number) field is configured as an Integer format. When a new `Tender Calendar` record is created, the system automatically queries the database to find the highest sequence number for that specific **Project** and increments it by 1.

### 2. Sequence Resilience (Deletion Handling)
To ensure sequence integrity, gaps in numbering are automatically resolved. If a user deletes a record, a background script runs (`on_trash` hook) and updates all subsequent records for that project by shifting their sequence numbers down.

### 3. Enhanced Gantt View Clarity
A background field, `gantt_title`, was added to the schema. Whenever a record is saved, the system dynamically constructs:
> `[Sequence Number] - [Category] - [Work Package]`

The Gantt chart uses this rich title to show the sequence order and the category group at a glance.

---

## 🏗️ Phase 4: Tower-Wise Custom Selection Engine

### 1. Block-Wise Checklist Dialog
When the project type is "Tower Wise", clicking the **"Generate Tower Tenders"** custom action button triggers a popup showing a checkbox list of remaining blocks linked to the project. Users can select specific blocks to generate tender lines for.

### 2. Deletion Resilience & Regeneration
- Dynamically queries only blocks that do not already have active tender records.
- If any block-specific tender record is deleted, that block is automatically restored to the checklist, allowing users to regenerate it at any time.

---

## 🔒 Phase 5: Workflow Roles & Security Policies

### 1. Custom DocPerms & Setup Script
- Running `setup_permissions.py` initializes 11 required roles and workspace permissions.
- Planning roles and System Managers have full permissions. Other collaborative roles (Architect, Quantity Surveyor, Procurement, Contracts, Project Team, Project Head, Tender Committee, Management) have view/edit permissions, but are restricted from creating or deleting documents.

### 2. Multi-State Approval Workflow
- Activated `"Tender Calendar Workflow"` on the doctype featuring 14 states (from `Tender Creation` to `Completed`).
- Integrates badge colors (Primary, Warning, Info, Success) for visual feedback.
- Restricts editing permissions on each state to the owner role designated for that lifecycle stage.

---

## 🛠️ Verification & Testing

### 1. Try Suggestion Mode:
1. Open a **Tender Calendar** record.
2. Set 'Cascading Mode' to **Suggestion**.
3. Enter a new (more delayed) **BOQ Submission Date (Actual)**.
4. Save the record and observe the interactive impact prompt.

### 2. Run Automated Verification Tests:
All 8 test cases can be run using the following command:
```bash
$ bench --site selfcare.tridasa.in execute realapp.tender.doctype.tender_calendar.test_tender_calendar.run_tests
```

**Test Execution Output:**
```text
test_autoname_and_insert (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_autoname_and_insert)
Test that the sequence sl_no is auto-generated and gantt_title is populated. ... ok
test_calendar_events_retrieval (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_calendar_events_retrieval)
Test get_calendar_events endpoint structure. ... ok
test_cascading_auto (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_cascading_auto)
Test that delaying the BOQ submission date cascades dates progressively in Auto mode. ... ok
test_generate_tower_tenders (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_generate_tower_tenders)
Test the Tower Wise generation engine with partial selection and deletion resilience. ... ok
test_permission_restrictions (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_permission_restrictions)
Test that only planning roles can create Tender Calendar docs. ... ok
test_report_sorting (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_report_sorting)
Test that all specified reports sort their data by sl_no asc. ... ok
test_sequence_trash_handling (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_sequence_trash_handling)
Test sequence re-ordering when a record is deleted. ... ok
test_workflow_transitions (realapp.tender.doctype.tender_calendar.test_tender_calendar.TestTenderCalendar.test_workflow_transitions)
Test that Tender Calendar workflow transitions states correctly using assigned roles. ... ok

----------------------------------------------------------------------
Ran 8 tests in 37.915s

OK
All tests passed successfully!
```

---

## 🗺️ Roadmap (Pending Features)

The following features are scheduled for future development sprints:

### Level 1: Predecessor Sequencing
- **Cross-Record Dependency Cascading**: Using sequence order to automatically check if a work package's timeline conflicts with its immediate predecessor and visually flag delay risks.

### Level 2: Stage-Gate Validation
- **Transition Constraints**: Enforcing hard validation rules at the Python layer to ensure transition actions cannot bypass chronological date checks.

### Level 3: ERPNext Integration & Alerts
- **Notification Engine**: Daily email/Slack alerts for upcoming 3-day deadlines.
- **RFQ Bridge**: Dynamic linkages to automatically initialize standard RFQs in ERPNext from a finalized Tender Calendar record.
