// Copyright (c) 2025, OneHash and contributors
// For license information, please see license.txt

frappe.ui.form.on("PineLabs Order", {
  refresh: function (frm) {
    addPineLabsOrderActions(frm);
  },
});

function addPineLabsOrderActions(frm) {
  if (frm.is_new()) return;

  addCancelOrderButton(frm);
  addRefreshOrderButton(frm);
}

function addCancelOrderButton(frm) {
  if (frm.doc.docstatus === 2) return;

  const BTN_LABEL = "Cancel Order";

  frm.page.remove_inner_button(BTN_LABEL);
  frm.page.add_inner_button(
    BTN_LABEL,
    () => {
      frappe.confirm(
        `<p>Are you sure you want to <strong>Cancel</strong> the order.</p>`,
        () => {
          frappe.call({
            method:
              "crm_pinelabs_integration.pine_labs.doctype.pinelabs_order.pinelabs_order.cancel_order",
            args: { order_id: frm.doc.name },
            freeze: true,
            freeze_message: "Cancelling PineLabs Order.",
            callback: function (res) {
              if (res.message === "success") {
                frappe.show_alert({
                  message: "Cancelled Order.",
                  indicator: "green",
                });
              }
            },
          });
        },
      );
    },
    null,
    "danger",
  );
}

function addRefreshOrderButton(frm) {
  if (frm.doc.docstatus === 1) return;

  const BTN_LABEL = "Refresh Order";

  frm.page.remove_inner_button(BTN_LABEL);
  frm.page.add_inner_button(
    BTN_LABEL,
    () => {
      frappe.call({
        method:
          "crm_pinelabs_integration.pine_labs.doctype.pinelabs_order.pinelabs_order.refresh_order_status",
        args: { order_id: frm.doc.name },
        freeze: true,
        freeze_message: "Refreshing PineLabs Order.",
        callback: function (res) {
          if (res.message === "success") {
            frappe.show_alert({
              message: "Order Refreshed.",
              indicator: "green",
            });
          }
        },
      });
    },
    null,
  );
}
