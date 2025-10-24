import frappe
from crm_pinelabs_integration.pine_labs.integration import (
    api,
    auth,
    utils,
    transformers,
)


def generate_order_id():
    return utils.generate_order_id()


def create_order(
    amount,
    store,
    terminal,
    sequence_number=1,
    order_id=None,
    payment_modes=None,
    auto_cancel_in_mins=None,
    customer_mobile=None,
    customer_email=None,
    upi_bank=None,
    original_order_id=None,
    throw=True,
):
    settings_doc = auth.get_settings()
    if not order_id:
        order_id = generate_order_id()
    if not sequence_number:
        sequence_number = 1

    order = api.create_order(
        {
            "TransactionNumber": order_id,
            "SequenceNumber": sequence_number,
            "AllowedPaymentMode": utils.get_allowed_payment_modes(payment_modes),
            "Amount": amount * 100,  # Convert to Paisa
            "UserID": frappe.session.user,
            "MerchantID": settings_doc.merchant_id,
            "SecurityToken": settings_doc.get_password("security_token"),
            "StoreID": utils.get_store_id(store),
            "ClientID": utils.get_client_id(terminal),
            "AutoCancelDurationInMinutes": auto_cancel_in_mins
            or settings_doc.auto_cancel_duration,
            "Customer Mobile Number": customer_mobile,
            "Customer Email ID": customer_email,
            "OriginalPlutusTransactionReferenceID": original_order_id,
            "BankCode": utils.get_bank_code(upi_bank) if upi_bank else None,
        }
    )

    if throw and order.get("ResponseCode") != 0:
        frappe.throw(order.get("ResponseMessage"))

    return order


def get_order_status(order_id=None, order_doc=None, throw=True):
    if not (order_id or order_doc):
        frappe.throw("Either of Order Id or Order Doc is required.")

    settings_doc = auth.get_settings()

    if not order_doc:
        order_doc = frappe.get_doc("PineLabs Order", order_id)

    order_status = api.get_order_status(
        {
            "MerchantID": settings_doc.merchant_id,
            "SecurityToken": settings_doc.get_password("security_token"),
            "ClientID": utils.get_client_id(order_doc.terminal),
            "StoreID": utils.get_store_id(order_doc.store),
            "PlutusTransactionReferenceID": order_doc.transaction_reference_id,
            "TransactionNumber": order_id,
        }
    )

    if throw and order_status.get("ResponseCode") != 0:
        frappe.throw(order_status.get("ResponseMessage"))

    return transformers.parse_order_res(order_status)


def cancel_order(order_id=None, order_doc=None, throw=True):
    if not (order_id or order_doc):
        frappe.throw("Either of Order Id or Order Doc is required.")

    settings_doc = auth.get_settings()

    if not order_doc:
        order_doc = frappe.get_doc("PineLabs Order", order_id)

    cancel_response = api.cancel_order(
        {
            "MerchantID": settings_doc.merchant_id,
            "SecurityToken": settings_doc.get_password("security_token"),
            "ClientID": utils.get_client_id(order_doc.terminal),
            "StoreID": utils.get_store_id(order_doc.store),
            "PlutusTransactionReferenceID": order_doc.transaction_reference_id,
            "Amount": order_doc.amount * 100,
        }
    )

    if throw and cancel_response.get("ResponseCode") != 0:
        frappe.throw(cancel_response.get("ResponseMessage"))

    return cancel_response
