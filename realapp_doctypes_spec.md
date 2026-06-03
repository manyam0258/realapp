# Realapp DocType Specification — Leads & Opportunity (Tridasa)

> **Purpose:** Single-file blueprint for an AI coding agent to create 8 standalone custom DocTypes in the Frappe app **`realapp`**, derived from the `All_Leads_Oppurtunity_Data_Reporting` workbook (sheets: *All Leads_Link*, *All Oppo_Base_link*, *Lookup data*).
>
> **Naming convention:** every custom business field on the Lead form is prefixed `ld_`; every custom field on the Opportunity form is prefixed `op_`. Master doctypes are prefixed `LD ` / `OP ` per the Lookup sheet's `Nature` column.

---

## Agent Instructions (read first)

1. **App / module:** All doctypes belong to app `realapp`, module **`Realapp`**. Do **not** create a separate app.
2. **Create in the exact order below (1 → 8).** Masters must exist before the Lead/Opportunity Link fields resolve; `Lead` must exist before `Opportunity`.
3. **Placement:** write each block to `realapp/realapp/realapp/doctype/<snake_name>/<snake_name>.json` and add an empty `__init__.py` (and the matching `<snake_name>.py` controller stub) in each folder. Folder snake_names: `ld_lead_type`, `ld_lead_source`, `ld_lead_stage`, `ld_lead_sub_source`, `op_opportunity_stage`, `op_opportunity_sub_source`, `lead`, `opportunity`.
4. **Then run:** `bench --site <site> migrate` (or import each JSON via *DocType > Menu > Import*).
5. **Do the 3 post-creation fixes** in the final section before importing workbook data.

### ⚠️ Critical: name collision
ERPNext ships native **`Lead`** and **`Opportunity`** doctypes. These standalone definitions reuse those names and **will collide** on any site with ERPNext installed. Before `migrate`, decide:
- **Option A (recommended):** rename to `Realapp Lead` / `Realapp Opportunity` (update each `"name"`, the folder, and the `op_lead_id` Link `options` on Opportunity → `Realapp Lead`).
- **Option B:** install on a site **without** ERPNext's CRM/Selling, keeping the bare names.

---

## DocType JSON blocks

### 1. LD Lead Type

*Lead-form master* — path: `realapp/realapp/realapp/doctype/ld_lead_type/ld_lead_type.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:lead_type",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "lead_type",
  "ld_short_name"
 ],
 "fields": [
  {
   "fieldname": "lead_type",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Lead Type",
   "reqd": 1,
   "unique": 1
  },
  {
   "fieldname": "ld_short_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Short Name"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "LD Lead Type",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "read": 1,
   "role": "Sales User"
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
```

### 2. LD Lead Source

*Lead-form master (has ld_partner vendor-grouping field)* — path: `realapp/realapp/realapp/doctype/ld_lead_source/ld_lead_source.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:lead_source",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "lead_source",
  "ld_short_name",
  "ld_partner"
 ],
 "fields": [
  {
   "fieldname": "lead_source",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Lead Source",
   "reqd": 1,
   "unique": 1
  },
  {
   "fieldname": "ld_short_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Short Name"
  },
  {
   "description": "Vendor / partner grouping used in reporting (e.g. 1. GenY, 2. 99 Acres, 4. Tridasa)",
   "fieldname": "ld_partner",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Partner / Vendor Group"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "LD Lead Source",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "read": 1,
   "role": "Sales User"
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
```

### 3. LD Lead Stage

*Lead-form master* — path: `realapp/realapp/realapp/doctype/ld_lead_stage/ld_lead_stage.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:lead_stage",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "lead_stage",
  "ld_short_name"
 ],
 "fields": [
  {
   "fieldname": "lead_stage",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Lead Stage",
   "reqd": 1,
   "unique": 1
  },
  {
   "fieldname": "ld_short_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Short Name"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "LD Lead Stage",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "read": 1,
   "role": "Sales User"
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
```

### 4. LD Lead Sub Source

*Lead-form master* — path: `realapp/realapp/realapp/doctype/ld_lead_sub_source/ld_lead_sub_source.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:lead_sub_source",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "lead_sub_source",
  "ld_short_name"
 ],
 "fields": [
  {
   "fieldname": "lead_sub_source",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Lead Sub Source",
   "reqd": 1,
   "unique": 1
  },
  {
   "fieldname": "ld_short_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Short Name"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "LD Lead Sub Source",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "read": 1,
   "role": "Sales User"
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
```

### 5. OP Opportunity Stage

*Opportunity-form master (ordered by stage_sl_no)* — path: `realapp/realapp/realapp/doctype/op_opportunity_stage/op_opportunity_stage.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:opportunity_stage",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "stage_sl_no",
  "opportunity_stage",
  "op_short_name"
 ],
 "fields": [
  {
   "description": "Sequence number of the stage (1 = SV Done ... 13 = Closed Lost)",
   "fieldname": "stage_sl_no",
   "fieldtype": "Int",
   "in_list_view": 1,
   "label": "Stage Sl No"
  },
  {
   "fieldname": "opportunity_stage",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Opportunity Stage",
   "reqd": 1,
   "unique": 1
  },
  {
   "description": "Reporting bucket (e.g. 2. Cost Sheet, 3. Booking Process, 5. Sale, 6. Lost)",
   "fieldname": "op_short_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Short Name"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "OP Opportunity Stage",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "read": 1,
   "role": "Sales User"
  }
 ],
 "sort_field": "stage_sl_no",
 "sort_order": "ASC",
 "states": [],
 "track_changes": 1
}
```

### 6. OP Opportunity Sub Source

*Opportunity-form master* — path: `realapp/realapp/realapp/doctype/op_opportunity_sub_source/op_opportunity_sub_source.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:opportunity_sub_source",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "opportunity_sub_source",
  "op_short_name"
 ],
 "fields": [
  {
   "fieldname": "opportunity_sub_source",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Opportunity Sub Source",
   "reqd": 1,
   "unique": 1
  },
  {
   "fieldname": "op_short_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Short Name"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "OP Opportunity Sub Source",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "read": 1,
   "role": "Sales User"
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
```

### 7. Lead

*Main form — 20 ld_ fields* — path: `realapp/realapp/realapp/doctype/lead/lead.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "field:ld_lead_id",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "sb_identification",
  "ld_lead_id",
  "ld_project",
  "ld_reporting_month",
  "cb_id_1",
  "ld_lead_type",
  "ld_lead_status",
  "ld_form_name",
  "sb_source",
  "ld_lead_source",
  "ld_lead_sub_source",
  "cb_source_1",
  "ld_channel_partner",
  "sb_contact",
  "ld_phone",
  "ld_unit_type",
  "cb_contact_1",
  "ld_qualification_criteria",
  "sb_ownership",
  "ld_lead_owner",
  "ld_pre_sales_team_member",
  "sb_dates",
  "ld_create_date",
  "ld_created_month",
  "cb_dates_1",
  "ld_last_modified",
  "ld_dropped_stage",
  "sb_referral",
  "ld_referred_by_name",
  "cb_ref_1",
  "ld_referred_by_phone"
 ],
 "fields": [
  {
   "fieldname": "sb_identification",
   "fieldtype": "Section Break",
   "label": "Identification"
  },
  {
   "fieldname": "ld_lead_id",
   "fieldtype": "Data",
   "label": "Lead Id",
   "reqd": 1,
   "unique": 1,
   "in_list_view": 1,
   "in_standard_filter": 1
  },
  {
   "fieldname": "ld_project",
   "fieldtype": "Data",
   "label": "Project",
   "default": "TRIDASA Rise",
   "in_standard_filter": 1
  },
  {
   "fieldname": "ld_reporting_month",
   "fieldtype": "Date",
   "label": "Reporting Month"
  },
  {
   "fieldname": "cb_id_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "ld_lead_type",
   "fieldtype": "Link",
   "label": "Lead Type",
   "options": "LD Lead Type",
   "in_standard_filter": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "ld_lead_status",
   "fieldtype": "Link",
   "label": "Lead Status",
   "options": "LD Lead Stage",
   "in_standard_filter": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "ld_form_name",
   "fieldtype": "Data",
   "label": "Form Name"
  },
  {
   "fieldname": "sb_source",
   "fieldtype": "Section Break",
   "label": "Source"
  },
  {
   "fieldname": "ld_lead_source",
   "fieldtype": "Link",
   "label": "Lead Source",
   "options": "LD Lead Source",
   "in_standard_filter": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "ld_lead_sub_source",
   "fieldtype": "Link",
   "label": "Lead Sub Source",
   "options": "LD Lead Sub Source"
  },
  {
   "fieldname": "cb_source_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "ld_channel_partner",
   "fieldtype": "Data",
   "label": "Channel Partner"
  },
  {
   "fieldname": "sb_contact",
   "fieldtype": "Section Break",
   "label": "Contact & Requirement"
  },
  {
   "fieldname": "ld_phone",
   "fieldtype": "Data",
   "label": "Phone",
   "options": "Phone"
  },
  {
   "fieldname": "ld_unit_type",
   "fieldtype": "Select",
   "label": "Unit Type",
   "options": "\n3 BHK\n4 BHK\nNA"
  },
  {
   "fieldname": "cb_contact_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "ld_qualification_criteria",
   "fieldtype": "Small Text",
   "label": "Qualification Criteria",
   "description": "May contain multiple values separated by ; (e.g. Location; Configuration)"
  },
  {
   "fieldname": "sb_ownership",
   "fieldtype": "Section Break",
   "label": "Ownership"
  },
  {
   "fieldname": "ld_lead_owner",
   "fieldtype": "Link",
   "label": "Lead Owner",
   "options": "Sales Person",
   "in_standard_filter": 1
  },
  {
   "fieldname": "ld_pre_sales_team_member",
   "fieldtype": "Link",
   "label": "Pre Sales Team Member",
   "options": "Sales Person"
  },
  {
   "fieldname": "sb_dates",
   "fieldtype": "Section Break",
   "label": "Dates"
  },
  {
   "fieldname": "ld_create_date",
   "fieldtype": "Date",
   "label": "Create Date"
  },
  {
   "fieldname": "ld_created_month",
   "fieldtype": "Date",
   "label": "Created Month"
  },
  {
   "fieldname": "cb_dates_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "ld_last_modified",
   "fieldtype": "Date",
   "label": "Last Modified"
  },
  {
   "fieldname": "ld_dropped_stage",
   "fieldtype": "Data",
   "label": "Dropped Stage"
  },
  {
   "fieldname": "sb_referral",
   "fieldtype": "Section Break",
   "label": "Referral"
  },
  {
   "fieldname": "ld_referred_by_name",
   "fieldtype": "Data",
   "label": "Referred By Name"
  },
  {
   "fieldname": "cb_ref_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "ld_referred_by_phone",
   "fieldtype": "Data",
   "label": "Referred By Phone",
   "options": "Phone"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "Lead",
 "naming_rule": "By fieldname",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "create": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "Sales User",
   "share": 1,
   "write": 1
  }
 ],
 "search_fields": "ld_phone,ld_lead_source,ld_lead_status",
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "title_field": "ld_lead_id",
 "track_changes": 1
}
```

### 8. Opportunity

*Main form — 13 op_ fields, links to Lead* — path: `realapp/realapp/realapp/doctype/opportunity/opportunity.json`

```json
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "naming_series:",
 "creation": "2026-06-03 00:00:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "sb_identification",
  "naming_series",
  "op_lead_id",
  "op_reporting_month",
  "cb_id_1",
  "op_lead_type",
  "op_stage",
  "op_bhk",
  "sb_source",
  "op_lead_source",
  "op_lead_sub_source",
  "cb_source_1",
  "op_vendor",
  "sb_ownership",
  "op_sales_team_member",
  "op_pre_sales_team_member",
  "sb_dates",
  "op_created_date",
  "cb_dates_1",
  "op_booking_date"
 ],
 "fields": [
  {
   "fieldname": "sb_identification",
   "fieldtype": "Section Break",
   "label": "Identification"
  },
  {
   "fieldname": "naming_series",
   "fieldtype": "Select",
   "label": "Series",
   "options": "OPP-.YYYY.-",
   "default": "OPP-.YYYY.-",
   "reqd": 1
  },
  {
   "fieldname": "op_lead_id",
   "fieldtype": "Link",
   "label": "Lead",
   "options": "Lead",
   "in_standard_filter": 1,
   "in_list_view": 1,
   "reqd": 1
  },
  {
   "fieldname": "op_reporting_month",
   "fieldtype": "Date",
   "label": "Reporting Month"
  },
  {
   "fieldname": "cb_id_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "op_lead_type",
   "fieldtype": "Link",
   "label": "Lead Type",
   "options": "LD Lead Type",
   "in_standard_filter": 1
  },
  {
   "fieldname": "op_stage",
   "fieldtype": "Link",
   "label": "Stage",
   "options": "OP Opportunity Stage",
   "in_standard_filter": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "op_bhk",
   "fieldtype": "Select",
   "label": "BHK",
   "options": "\n3 BHK\n4 BHK\nNA"
  },
  {
   "fieldname": "sb_source",
   "fieldtype": "Section Break",
   "label": "Source"
  },
  {
   "fieldname": "op_lead_source",
   "fieldtype": "Link",
   "label": "Lead Source",
   "options": "LD Lead Source",
   "in_standard_filter": 1,
   "in_list_view": 1
  },
  {
   "fieldname": "op_lead_sub_source",
   "fieldtype": "Link",
   "label": "Lead Sub Source",
   "options": "OP Opportunity Sub Source"
  },
  {
   "fieldname": "cb_source_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "op_vendor",
   "fieldtype": "Data",
   "label": "Vendor",
   "description": "Partner / vendor grouping (mirrors LD Lead Source -> Partner)"
  },
  {
   "fieldname": "sb_ownership",
   "fieldtype": "Section Break",
   "label": "Ownership"
  },
  {
   "fieldname": "op_sales_team_member",
   "fieldtype": "Link",
   "label": "Sales Team Member",
   "options": "Sales Person",
   "in_standard_filter": 1
  },
  {
   "fieldname": "op_pre_sales_team_member",
   "fieldtype": "Link",
   "label": "Pre Sales Team Member",
   "options": "Sales Person"
  },
  {
   "fieldname": "sb_dates",
   "fieldtype": "Section Break",
   "label": "Dates"
  },
  {
   "fieldname": "op_created_date",
   "fieldtype": "Date",
   "label": "Created Date"
  },
  {
   "fieldname": "cb_dates_1",
   "fieldtype": "Column Break"
  },
  {
   "fieldname": "op_booking_date",
   "fieldtype": "Date",
   "label": "Booking Date"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-06-03 00:00:00.000000",
 "module": "Realapp",
 "name": "Opportunity",
 "naming_rule": "By \"Naming Series\" field",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  },
  {
   "create": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "Sales User",
   "share": 1,
   "write": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "track_changes": 1
}
```

---

## Post-Creation Fixes (before importing workbook data)

1. **Resolve the Lead/Opportunity name collision** (see Critical note above). If using Option A, the `op_lead_id` field on Opportunity must point its `options` to `Realapp Lead`.

2. **Seed `Sales Person` records.** The person fields (`ld_lead_owner`, `ld_pre_sales_team_member`, `op_sales_team_member`, `op_pre_sales_team_member`) are `Link → Sales Person`. Every distinct name in the *Lead Owner / Pre Sales / Sales Team Member* columns of both sheets must exist as a `Sales Person` (or be created on the fly during import), or Link validation fails.

3. **Data cleanup during import.**
   - Dates are `dd/mm/yyyy` strings → reformat before `frappe.utils.getdate` (its default parser is mm/dd).
   - `Booking Date == 0` → treat as empty/null.
   - `BHK` / `Unit Type == "NA"` → maps to the `NA` Select option (already defined).
   - On the Opportunity sheet, `Lead Source` is the long name while the Lookup `Vendor`/`Partner` column is the short grouping → store the grouping via `LD Lead Source.ld_partner`, not raw text, when populating `op_vendor`.

## Master data to load (from Lookup sheet)

| Master | Approx. distinct values |
|---|---|
| LD Lead Type | 4 — Pre-Sales, Walk In, Channel Partner, Referral |
| LD Lead Source | ~40 — 99acres, Magicbricks, Housing, Hoarding, Website, Meta, Google, … (with partner group) |
| LD Lead Stage | 8 — New, Assigned, Contacted, Qualified, SV Planned, Re-Enquiry, Converted, Dropped |
| LD Lead Sub Source | ~41 — Nallagandla location, Tellapur location, Credai expo, Website-MS-*, … |
| OP Opportunity Stage | 13 — SV Done → Cost Sheet Generated → … → Demand Letter → Closed Lost (sl_no 1–13) |
| OP Opportunity Sub Source | ~27 — Nallagandla location, Tellapur location, Credai expo, … |
