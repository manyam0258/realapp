# Copyright (c) 2026, surendhranath and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Tender(Document):

    def validate(self):
        if self.order_type == "Service":
            self.indigenous_import = "NA"