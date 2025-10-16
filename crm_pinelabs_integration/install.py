import frappe


def after_install():
    add_upi_banks()
    add_payment_modes()

    frappe.db.commit()


def add_upi_banks():
    from crm_pinelabs_integration.config.upi_banks import UPI_BANKS

    for upi_bank in UPI_BANKS:
        if not frappe.db.exists("PineLabs UPI Bank", upi_bank["bank_code"]):
            frappe.get_doc({"doctype": "PineLabs UPI Bank", **upi_bank}).save()


def add_payment_modes():
    from crm_pinelabs_integration.config.payment_modes import PAYMENT_MODES

    for payment_mode in PAYMENT_MODES:
        if not frappe.db.exists("PineLabs Payment Mode", payment_mode["mode_id"]):
            frappe.get_doc({"doctype": "PineLabs Payment Mode", **payment_mode}).save()
