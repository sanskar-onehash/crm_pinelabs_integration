import frappe

INTEGRATION_TYPE = "CloudBasedIntegration"
API_VERSION = "V1"


def get_base_uri():
    settings = get_settings()
    return f"{settings.base_uri}/{INTEGRATION_TYPE}/{API_VERSION}"


def get_settings():
    settings = frappe.get_single("PineLabs Settings")
    if not settings.enabled:
        settings_url = frappe.utils.get_url_to_list("PineLabs Settings")
        frappe.throw(
            f"PineLabs is not enabled. Please check <a href='{settings_url}'>PineLabs Settings.</a>"
        )
    return settings
