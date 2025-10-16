# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PineLabsSettings(Document):

    def validate(self):
        if self.enabled:
            self.validate_base_uri()

    def validate_base_uri(self):
        frappe.utils.validate_url(self.base_uri, throw=True)

        if self.base_uri.endswith("/"):
            self.base_uri = self.base_uri[:-1]
