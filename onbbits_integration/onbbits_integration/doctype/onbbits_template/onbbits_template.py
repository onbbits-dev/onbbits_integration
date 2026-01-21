# Copyright (c) 2025, It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from onbbits_integration.onbbits_api import create_template_in_onbbits
import re


class OnBBitsTemplate(Document):
    def validate(self):
        if len(self.template_buttons) > 10:
            frappe.throw("You can add a maximum of 10 rows in the table.")

        header_text = self.header_text or ""

        # Find all parameters like {{1}}, {{2}}, etc.
        params = re.findall(r"\{\{\d+\}\}", header_text)

        if not params:
            return  # No parameters, OK

        # If parameters exist, only one parameter allowed and must be {{1}}
        if len(params) > 1 or params[0] != "{{1}}":
            frappe.throw("Header Text can contain only one parameter and it must be {{1}}.")

        # If {{1}} exists, header parameter field becomes mandatory
        if not self.header_parameter:
            frappe.throw("Please fill Header Parameter because Header Text contains {{1}}.")

    def on_submit(self):
        if self.source != "OnBBits":
            create_template_in_onbbits(self)
        