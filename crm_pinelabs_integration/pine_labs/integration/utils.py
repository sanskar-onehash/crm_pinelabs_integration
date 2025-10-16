import frappe


def generate_order_id():
    return frappe.generate_hash()


def get_payment_mode_id(payment_mode):
    return frappe.db.get_value("PineLabs Payment Mode", payment_mode, "mode_id")


def get_allowed_payment_modes(payment_modes=None):
    if isinstance(payment_modes, str):
        payment_modes = [payment_modes]
    if isinstance(payment_modes, list):
        payment_mode_ids = set()
        for payment_mode in payment_modes:
            payment_mode_id = get_payment_mode_id(payment_mode)
            if payment_mode_id == 0:
                payment_modes = None
                break
            payment_mode_ids.add(payment_mode_id)

        payment_modes = payment_mode_ids
    if not payment_modes:
        payment_modes = ["0"]  # Allow all modes enabled on the Plutus terminal.

    return ",".join(payment_modes)


def get_store_id(store):
    if not frappe.db.exists("PineLabs Store", store):
        frappe.throw("Store not found in the system.")

    # Currently store id is used as PineLabs Store Name
    return store


def get_bank_code(upi_bank):
    if not frappe.db.exists("PineLabs UPI Bank", upi_bank):
        frappe.throw("UPI Bank not found in the system.")

    # Currently bank code is used as PineLabs UPI Bank Name
    return upi_bank


def get_client_id(terminal):
    if not frappe.db.exists("PineLabs Terminal", terminal):
        frappe.throw("Terminal not found in the system.")

    # Currently client id is used as PineLabs Terminal Name
    return terminal
