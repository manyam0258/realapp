# Implementation Plan - Sequence & Gantt Enhancements

This plan outlines the enhancements to the `Tender Calendar` DocType to support robust auto-sequencing (`sl_no`) and a more informative Gantt View, as requested.

## User Review Required

> [!IMPORTANT]
> **Sequence Recalculation on Deletion**: 
> I propose that when a user deletes a record (e.g., Sequence No. 2), the system will automatically shift all subsequent records for that same project down by 1 (e.g., Sequence No. 3 becomes 2, No. 4 becomes 3). This ensures there are never any gaps in your numbering. 

## Open Questions

> [!WARNING]
> **Cascading Effect Across Tenders**: You mentioned, *"sequence should work properly so that the cascading effect also works properly"*. 
> Currently, the cascading effect shifts dates **within a single tender** (e.g., BOQ delay -> Contract delay). 
> **Question**: Do you eventually want delays to cascade **across different tenders** based on this sequence? (e.g., If Tender Sequence No.1 is delayed, automatically shift the start dates for Tender Sequence No.2?) 
> For now, this plan ensures the sequence is rock-solid to support such future logic.

## Proposed Changes

### Tender Calendar DocType (Schema)

#### [MODIFY] [tender_calendar.json](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.json)
- **Change `sl_no` FieldType**: Change from `Data` to `Int` so it sorts correctly natively.
- **Add `gantt_title` Field**: A new read-only/hidden `Data` field that will store the combined string (Sequence - Category - Work Package) for the Gantt chart.

### Controller Logic

#### [MODIFY] [tender_calendar.py](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar.py)
- **`before_insert` Hook**: 
  - Automatically calculate `sl_no` by finding the maximum `sl_no` for the current `project` and adding 1.
- **`validate` Hook**:
  - Populate the `gantt_title` field dynamically: `f"{self.sl_no} - {self.category} - {self.work_package}"`.
- **`on_trash` Hook**:
  - Implement a sequence recalculation script. When a record is deleted, fetch all remaining records for the same `project` with an `sl_no` greater than the deleted record, and subtract 1 from their `sl_no`.

### Gantt View Configuration

#### [MODIFY] [tender_calendar_gantt.js](file:///home/demo/frappe-bench2/apps/realapp/realapp/tender/doctype/tender_calendar/tender_calendar_gantt.js)
- Update the `field_map.title` property from `"work_package"` to `"gantt_title"`. This will render the complete, descriptive sequence string on the timeline.

## Verification Plan

### Manual Verification
1. **Creation**: Create two new Tender Calendar records for a project. Verify they automatically receive `sl_no` 1 and 2 respectively.
2. **Deletion**: Create a 3rd record (`sl_no` 3). Delete record 2. Verify that record 3 automatically updates to `sl_no` 2.
3. **Gantt View**: Open the Gantt view and verify the task title displays as "1 - [Category] - [Work Package]".
