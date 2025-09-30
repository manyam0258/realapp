# Copyright (c) 2025, surendhranath and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RealappSettings(Document):
	def validate(self):
        # Ensure GST and TDS have sensible defaults
		self.gst_rate = self.gst_rate
		self.tds_rate = self.tds_rate
		