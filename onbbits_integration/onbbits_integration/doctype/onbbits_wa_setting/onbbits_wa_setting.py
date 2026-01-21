# Copyright (c) 2025, It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_abbr


class OnBBitsWASetting(Document):
	def before_insert(doc):
		# Generate base abbreviation from app_name with max 3 chars
		base_abbr = get_abbr(doc.app_name, max_len=3).upper()

		abbr = base_abbr
		counter = 1

		# Ensure unique abbreviation
		while frappe.db.exists("OnBBits WA Setting", {"abbr": abbr}):
			abbr = f"{base_abbr}{counter}"
			counter += 1

		doc.abbr = abbr

	def validate(self):
		if frappe.db.exists("OnBBits WA Setting", {"api_key": self.api_key, "name": ["!=", self.name]}):
			frappe.throw("API Key must be unique. The provided API Key already exists.")