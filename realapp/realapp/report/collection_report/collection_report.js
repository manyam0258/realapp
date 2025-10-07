// Copyright (c) 2025, surendhranath and contributors
// For license information, please see license.txt
/*
frappe.query_reports["Collection Report"] = {
	"filters": [

	]
};
*/
frappe.query_reports["Collection Report"] = {
  "filters": [
    {
      "fieldname": "company",
      "label": __("Company"),
      "fieldtype": "Link",
      "options": "Company"
    },
    {
      "fieldname": "project",
      "label": __("Project"),
      "fieldtype": "Link",
      "options": "Project"
    },
	    {
      "fieldname": "customer",
      "label": __("Customer"),
      "fieldtype": "Link",
      "options": "Customer"
    },    {
      "fieldname": "unit_name",
      "label": __("Unit"),
      "fieldtype": "Link",
      "options": "Unit"
    },
    {
      "fieldname": "block",
      "label": __("Block"),
      "fieldtype": "Data"
    },
    {
      "fieldname": "milestone",
      "label": __("Milestone"),
      "fieldtype": "Data"
    },
    {
      "fieldname": "milestone_item",
      "label": __("Milestone Item"),
      "fieldtype": "Link",
      "options": "Item"
    }
  ]
};
