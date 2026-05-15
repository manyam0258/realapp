# Copyright (c) 2026, Antigravity and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, date_diff

class TenderCalendar(Document):
	def autoname(self):
		settings = frappe.get_single("Tender Settings")
		if settings.naming_method == "Work Package":
			if not self.work_package:
				frappe.throw(_("Work Package name is required for naming"))
			self.name = self.work_package
		else:
			from frappe.model.naming import make_autoname
			self.name = make_autoname(self.naming_series)

	def before_insert(self):
		if not self.sl_no:
			max_sl_no = frappe.db.sql("""
				SELECT MAX(FLOOR(sl_no)) FROM `tabTender Calendar` 
				WHERE project = %s
			""", self.project)[0][0]
			self.sl_no = float((max_sl_no or 0) + 1)

	def validate(self):
		self.calculate_delay_and_impact()
		self.handle_cascading()
		self.gantt_title = f"{self.sl_no or ''} - {self.category or ''} - {self.work_package or ''}".strip(" - ")

	def on_trash(self):
		if self.sl_no and self.project:
			if self.sl_no % 1 != 0:
				# Sub-item deletion: shift siblings down
				parent_sl_no = int(self.sl_no)
				frappe.db.sql("""
					UPDATE `tabTender Calendar`
					SET sl_no = ROUND(sl_no - 0.1, 1)
					WHERE project = %s 
					AND sl_no > %s 
					AND sl_no < %s
				""", (self.project, self.sl_no, parent_sl_no + 1))
			else:
				# Master item deletion: shift all downstream masters and their subs
				frappe.db.sql("""
					UPDATE `tabTender Calendar`
					SET sl_no = ROUND(sl_no - 1, 1)
					WHERE project = %s AND sl_no > %s
				""", (self.project, self.sl_no))

	def calculate_delay_and_impact(self):
		"""Computes delay_days and impact_level based on target_date vs today or actuals."""
		if self.target_date and not self.actual_work_start:
			today = getdate()
			if today > getdate(self.target_date):
				self.delay_days = date_diff(today, self.target_date)
			else:
				self.delay_days = 0
		
		# Impact Logic
		if self.delay_days:
			if self.delay_days < 5:
				self.impact_level = "Low"
			elif self.delay_days < 10:
				self.impact_level = "Medium"
			elif self.delay_days < 20:
				self.impact_level = "High"
			else:
				self.impact_level = "Critical"
		else:
			self.impact_level = "Low"

	def handle_cascading(self):
		"""Handles the cascading engine if enabled in settings and record."""
		settings = frappe.get_single("Tender Settings")
		if not settings.enable_cascading or self.cascading_mode == "Manual":
			return

		# Only run Auto cascading on save if mode is Auto
		if settings.default_mode == "Auto" or self.cascading_mode == "Auto":
			self.apply_auto_cascade()

	def apply_auto_cascade(self):
		"""
		Implements progressive date shifting:
		If BOQ is delayed by D days:
		- Tender Issue -> +D
		- Approval -> +D+2
		- Contract -> +D+5
		- Mobilization -> +D+10
		"""
		# We need to detect which date was shifted. 
		# For simplification in this phase, we compare with the database version.
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if not old_doc: return

			if self.boq_submission_date != old_doc.boq_submission_date:
				delta = date_diff(self.boq_submission_date, old_doc.boq_submission_date)
				if delta > 0:
					if self.tender_issue_date:
						self.tender_issue_date = add_days(self.tender_issue_date, delta)
					if self.approval_date:
						self.approval_date = add_days(self.approval_date, delta + 2)
					if self.contract_date:
						self.contract_date = add_days(self.contract_date, delta + 5)
					if self.mobilization_date:
						self.mobilization_date = add_days(self.mobilization_date, delta + 10)
					if self.target_date:
						self.target_date = add_days(self.target_date, delta + 10)

					self.delay_info = f"Cascaded delay from BOQ: {delta} days"


@frappe.whitelist()
def get_calendar_events(start, end, filters=None):
	"""Returns 5 events per Tender Calendar record for the Unified View."""
	from frappe.desk.reportview import get_filters_cond
	
	conditions = get_filters_cond("Tender Calendar", filters, [])
	
	events = []
	data = frappe.db.sql(f"""
		SELECT 
			name, work_package, pre_bid_date, tender_issue_date, 
			approval_date, contract_date, mobilization_date, project_status
		FROM `tabTender Calendar`
		WHERE (pre_bid_date BETWEEN '{start}' AND '{end}'
			OR tender_issue_date BETWEEN '{start}' AND '{end}'
			OR approval_date BETWEEN '{start}' AND '{end}'
			OR contract_date BETWEEN '{start}' AND '{end}'
			OR mobilization_date BETWEEN '{start}' AND '{end}')
		{conditions}
	""", as_dict=True)

	for d in data:
		# Mapping 5 events
		event_types = [
			("pre_bid_date", "Pre-Bid", "#3498db"),
			("tender_issue_date", "Issue", "#e67e22"),
			("approval_date", "Approval", "#2ecc71"),
			("contract_date", "Contract", "#9b59b6"),
			("mobilization_date", "Mobilization", "#e74c3c")
		]
		
		for field, label, color in event_types:
			if d.get(field):
				events.append({
					"name": d.name,
					"start": d.get(field),
					"end": d.get(field),
					"title": f"[{label}] {d.work_package}",
					"color": color,
					"allDay": 1
				})
				
	return events

@frappe.whitelist()
def generate_tower_tenders(docname):
	master_doc = frappe.get_doc("Tender Calendar", docname)
	
	if master_doc.project_type != "Tower Wise":
		frappe.throw(_("Can only generate sub-tenders for 'Tower Wise' projects."))
	if master_doc.get("towers_generated"):
		frappe.throw(_("Tower Tenders have already been generated for this record."))
		
	# Get blocks
	blocks = frappe.get_all("Block", filters={"project": master_doc.project}, fields=["name", "tower_name", "block"])
	if not blocks:
		frappe.throw(_("No Blocks found for Project {0}").format(master_doc.project))
		
	for index, block in enumerate(blocks):
		new_doc = frappe.copy_doc(master_doc)
		# Keep the same sl_no as the parent but append .1, .2, etc.
		new_sl_no = round(float(master_doc.sl_no) + ((index + 1) * 0.1), 1)
		new_doc.sl_no = new_sl_no
		
		# Update work package and block reference
		tower_suffix = block.tower_name or block.name
		new_doc.work_package = f"{master_doc.work_package} - {tower_suffix}"
		new_doc.block = block.name
		new_doc.is_template = 0
		new_doc.towers_generated = 0
		
		# Optionally switch to Project type to prevent endless generation
		new_doc.project_type = "Project"
		
		new_doc.insert()
		
	# Mark the original as template and generated
	master_doc.db_set("towers_generated", 1)
	master_doc.db_set("is_template", 1)
	
	return True
