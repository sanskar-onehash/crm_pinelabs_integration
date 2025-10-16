# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PineLabsStore(Document):

    def validate(self):
        self.validate_default()

    def validate_default(self):
        if frappe.db.exists(
            "PineLabs Store", {"is_default": 1, "name": ["!=", self.name]}
        ):
            frappe.throw(
                "Default PineLabs Store already exists. You can only have one."
            )
