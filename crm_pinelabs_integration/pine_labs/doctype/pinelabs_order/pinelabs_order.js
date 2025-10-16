// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("PineLabs Order", {
  refresh(frm) {},
});

function addPineLabsOrderActions(frm) {
  if (frm.is_new()) {
    addCancelButton(frm);
  }
}

function addCancelButton(frm) {
  if (frm.docstatus) {
  }
}
