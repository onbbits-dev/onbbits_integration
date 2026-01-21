# Copyright (c) 2025, It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class OnBBitsTemplateTrigger(Document):
	def validate(self):
		if frappe.db.exists("OnBBits Template Trigger", {"reference_doctype": self.reference_doctype, "event":self.event, "disabled":0, "name": ["!=", self.name]}):
			frappe.throw("For this Reference Doctype and Event, a Template Trigger already exists.")
		
		for row in self.template_parameters:
			if row.static_value and row.reference_field:
				frappe.throw(
					f"Row {row.idx}: You cannot set both Static Value and Reference Field"
				)

			if not row.static_value and not row.reference_field:
				frappe.throw(
					f"Row {row.idx}: Either Static Value or Reference Field is required"
				)

