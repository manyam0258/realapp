# Master Walkthrough: Tender Management Module

Welcome to the Tender Management module. This module provides a robust, data-driven engine for procurement planning and execution. This walkthrough demonstrates the sequence of features developed and outlines the path forward.

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

### 1. Intelligent Date Management (Cascading Engine)
- **Auto Mode**: Automatically shifts downstream dates when the `BOQ Submission Date` is delayed. It follows a progressive buffer logic:
    - Tender Issue: +D
    - Approval: +D+2
    - Contract: +D+5
    - Mobilization/Target: +D+10
- **Suggestion Mode**: Detects date changes in the browser and prompts the user to apply the calculated shift across the lifecycle.
- **Manual Mode**: Allows independent date management without automatic shifting.

### 2. Intelligence & Validation
- **Impact Engine**: Calculates `delay_days` and `impact_level` (Low, Medium, High, Critical) automatically on save based on the `Target Date`.
- **Chronological Guardrails**: Real-time warnings if dates are entered out of sequence (e.g., Contract before Approval).

---

## 🚀 Phase 3: Sequence & Gantt Enhancements

### 1. Robust Sequence Auto-Generation
The `sl_no` (Serial Number) field has been successfully migrated to an Integer format. 
When a new `Tender Calendar` record is created, the system automatically queries the database to find the highest sequence number for that specific **Project** and increments it by 1. 

### 2. Sequence Resilience (Deletion Handling)
To ensure sequence integrity and support report logic, gaps in numbering are automatically resolved. 
If a user deletes a record (e.g., Sequence 2), a background script runs immediately (`on_trash` hook) and updates all subsequent records for that project by subtracting 1 from their sequence number. This guarantees that the sequence is always unbroken and sequential.

### 3. Enhanced Gantt View Clarity
A new background field, `gantt_title`, was added to the schema. Whenever a record is saved, the system dynamically constructs a rich title:
> `[Sequence Number] - [Category] - [Work Package]`

The Gantt chart configuration has been updated to use this new rich title instead of just the Work Package name. This means when you look at the Gantt timeline, you immediately see the sequence order and the category group.

---

## 🛠️ Verification & Testing

> [!TIP]
> **Try Suggestion Mode**:
> 1. Open a **Tender Calendar** record.
> 2. Set 'Cascading Mode' to **Suggestion**.
> 3. Enter a new (more delayed) **BOQ Submission Date (Actual)**.
> 4. Save the record and observe the interactive impact prompt.

> [!SUCCESS]
> **Check the Workspace**: All reports and views are linked in the new "Tender" Workspace for easy access. The module is ready for live procurement tracking.

---

## 🗺️ Roadmap (Pending Features)

The following features are scheduled for the next development sprints:

### Level 1: Deep Logic & Sequence Intelligence
- **Cross-Record Cascading**: Using the sequence logic to compare a work package's timeline against its immediate predecessor and cascade delays across different tenders.
- **Recursive Impact**: Automatic shifting of the *entire* chain with weighted durations.
- **Stage-Gate Locking**: Preventing milestones from being marked "Complete" if previous dates are invalid.

### Level 2: Governance (Workflow)
- **Approval Flow**: Formalized state transitions (Draft → Under Review → Finalized).
- **Audit Logging**: Tracking who changed which date and why (override reasons).

### Level 3: Integration & Notifications
- **ERPNext Bridge**: Links to standard RFQ and Purchase Order DocTypes.
- **Deadline Alerts**: Scheduled daily notifications for upcoming 3-day deadlines.
