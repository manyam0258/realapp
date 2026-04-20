# Sales Booking Data Attachments Task Tracker

- `[x]` Create `SBD Attachment` Child DocType
- `[x]` Add fields to `SBD Attachment`:
  - `attachment_type` (Select)
  - `attachment` (Attach)
- `[x]` Modify `Sales Booking Data` DocType
  - `[x]` Add `attachments_tab` (Tab Break)
  - `[x]` Add single attachment fields (Attach type)
  - `[x]` Add `sbd_attachments` (Table type, linked to `SBD Attachment`)
- `[x]` Verify changes via frappe bench execute
- `[x]` Create walkthrough.md
