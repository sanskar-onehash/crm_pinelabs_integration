import frappe


def get_or_throw(object, key):
    value = object.get(key)
    if not value:
        frappe.throw(f"{key} not found")
    return value


def ensure_parsed(value: list | dict | str | None) -> list | dict | None:
    if isinstance(value, str):
        return frappe.json.loads(value)
    return value
