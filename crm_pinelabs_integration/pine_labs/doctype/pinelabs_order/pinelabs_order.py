# Copyright (c) 2025, OneHash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from crm_pinelabs_integration import utils
from crm_pinelabs_integration.pine_labs.integration import service
from erpnext import get_default_company
from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry


class PineLabsOrder(Document):

    def autoname(self):
        if not self.order_id:
            self.order_id = service.generate_order_id()
        self.name = self.order_id

    def before_save(self):
        if self.get("reference_fieldname") or self.get("reference_pe_fieldname"):
            if not (self.get("reference_type") or self.get("reference_link")):
                frappe.throw("Reference Type and Doc are required.")

    def before_submit(self):
        if self.status != "Approved":
            frappe.throw("Order status should be Success to submit the order.")

        pe = self.create_order_pe(ignore_permissions=True)
        pe.run_method("before_submit")
        pe = pe.save(ignore_permissions=True)

        self.set("payment_entry", pe.name)

        reference_pe_fieldname = self.get("reference_pe_fieldname")
        if reference_pe_fieldname:
            reference_doc = frappe.get_doc(
                self.get("reference_type"), self.get("reference_link")
            )
            reference_doc.set(reference_pe_fieldname, pe.name)
            reference_doc.save(ignore_permissions=True)

    def before_insert(self):
        reference_fieldname = self.get("reference_fieldname")
        if reference_fieldname:
            reference_doc = frappe.get_doc(
                self.get("reference_type"), self.get("reference_link")
            )
            reference_doc.set(reference_fieldname, self.name)
            reference_doc.save(ignore_permissions=True)

    def refresh_order_details(self):
        if self.docstatus == 0:
            updated_order_status = service.get_order_status(
                self.order_id, self, throw=False
            )
            if updated_order_status.get("ResponseCode") != 0:
                response_message = updated_order_status.get("ResponseMessage")
                if response_message == "INVALID TRANSACTION NUMBER":
                    self.cancel_order(ignore_permissions=True)
                    return self
                frappe.throw(response_message)

            updated_transaction_status = updated_order_status.get("ResponseMessage")

            if updated_transaction_status == "TXN APPROVED":
                self.status = "Approved"
                self.update(updated_order_status.get("TransactionData"))
                # TODO: Map all payment modes
                if self.payment_mode == "CASH":
                    self.mode_of_payment = "Cash"
                self.save()
                self.submit()
            elif updated_transaction_status != self.pinelabs_status:
                self.pinelabs_status = updated_transaction_status
                self.save()
        return self

    def cancel_order(self, ignore_permissions=False):
        if not ignore_permissions:
            self.check_permission("cancel")
        cancel_result = service.cancel_order(order_doc=self, throw=False)
        response_message = cancel_result.get("ResponseMessage")

        if response_message in ["APPROVED", "TRANSACTION NOT FOUND"]:
            try:
                if self.docstatus == 0:
                    frappe.db.set_value(
                        "PineLabs Order",
                        self.name,
                        "docstatus",
                        1,
                        update_modified=False,
                    )
                    self.reload()

                if self.payment_entry:
                    pe_doc = frappe.get_doc("Payment Entry", self.payment_entry)
                    if pe_doc.docstatus == 0:
                        frappe.db.set_value(
                            "Payment Entry",
                            pe_doc.name,
                            "docstatus",
                            1,
                            update_modified=False,
                        )
                        pe_doc.reload()
                    if pe_doc.docstatus != 2:
                        pe_doc.flags.ignore_permissions = True
                        pe_doc.cancel()

                if self.docstatus != 2:
                    self.flags.ignore_permissions = ignore_permissions
                    self.cancel()
            except Exception as e:
                frappe.msgprint(
                    "Order Cancelled on PineLabs, but error occured while cancelling Payment Entry."
                )
                raise e
        elif cancel_result.get("ResponseCode") != 0:
            frappe.throw(response_message)
        return "success"

    def create_order_pe(self, ignore_permissions=False):
        pe = get_payment_entry(
            self.doctype,
            self.name,
            party_amount=self.amount,
            party_type="Customer",
            payment_type="Receive",
            reference_date=self.transaction_date,
            ignore_permissions=ignore_permissions,
        )

        # get_payment_entry sets PineLabs Order as reference
        pe.update(
            {
                "references": [],
                "docstatus": 1,
                "owner": self.owner,
                "reference_no": self.tid,
            }
        )
        for invoice in self.get("reference_invoices") or []:
            invoice_type = invoice.get("invoice_type")
            invoice_name = invoice.get("invoice")
            invoice_amount = frappe.db.get_value(
                invoice_type, invoice_name, "grand_total"
            )
            pe.append(
                "references",
                {
                    "reference_doctype": invoice_type,
                    "reference_name": invoice_name,
                    "allocated_amount": invoice_amount,
                },
            )

        return pe


@frappe.whitelist()
def create_order(
    order_amount=0,
    order_currency="INR",
    sequence_number=1,
    customer_details={},
    invoices=None,
    store=None,
    terminal=None,
    payment_modes=None,
    reference_doctype=None,
    reference_name=None,
    reference_fieldname=None,
    reference_pe_fieldname=None,
    auto_cancel_in_mins=None,
    upi_bank=None,
    original_order_id=None,
):
    customer_details = utils.ensure_parsed(customer_details)
    invoices = utils.ensure_parsed(invoices)
    payment_modes = utils.ensure_parsed(payment_modes)

    if not store:
        store = frappe.db.exists("PineLabs Store", {"is_default": 1})
    if not store:
        frappe.throw("No PineLabs Store found.")

    if not frappe.db.exists(
        "PineLabs Terminals",
        {
            "terminal": terminal,
            "parenttype": "PineLabs Store",
            "parent": store,
            "parentfield": "terminals",
        },
    ):
        frappe.throw(
            "Invalid Terminal, please check if terminal is selected in the PineLabs Store."
        )

    customer_id = customer_details.get("customer_id")
    invoices = invoices or []
    company = None

    if invoices:
        parsed = parse_reference_invoices(invoices, order_currency, customer_id)
        order_amount = parsed["amount"]
        order_currency = parsed["currency"]
        invoices = parsed["invoices"]
        company = parsed["company"]
        customer_id = parsed["customer"]
    elif not order_amount:
        frappe.throw("Either invoices or order_amount must be provided.")

    if not customer_id:
        frappe.throw("No Customer Found.")

    if not company:
        company = get_default_company()

    order_id = service.generate_order_id()

    order_doc = frappe.get_doc(
        {
            "doctype": "PineLabs Order",
            "order_id": order_id,
            "currency": order_currency,
            "amount": order_amount,
            "customer": customer_id,
            "reference_invoices": invoices,
            "company": company,
            "reference_type": reference_doctype,
            "reference_link": reference_name,
            "reference_fieldname": reference_fieldname,
            "reference_pe_fieldname": reference_pe_fieldname,
            "cashier": frappe.session.user,
            "store": store,
            "terminal": terminal,
        }
    )

    if not payment_modes:
        payment_modes = ["0"]  # Set "All Modes" or Mode 0 as default
    for payment_mode in payment_modes:
        order_doc.append("payment_modes", {"payment_mode": payment_mode})

    if not order_doc.has_permission("create"):
        frappe.throw("User don't have permissions for PineLabs Order.")

    pinelabs_order = service.create_order(
        amount=order_amount,
        store=store,
        terminal=terminal,
        sequence_number=sequence_number,
        order_id=order_id,
        payment_modes=payment_modes,
        auto_cancel_in_mins=auto_cancel_in_mins,
        customer_mobile=customer_details.get("customer_mobile"),
        customer_email=customer_details.get("customer_email"),
        upi_bank=upi_bank,
        original_order_id=original_order_id,
    )

    order_doc.update(
        {
            "transaction_reference_id": pinelabs_order.get(
                "PlutusTransactionReferenceID"
            ),
        }
    )

    order_doc.insert()

    # Commit because order is created on PineLabs
    # Hence cannot miss in system incase of Get request
    frappe.db.commit()
    return order_doc.as_dict()


@frappe.whitelist()
def refresh_order_status(order_id):
    return frappe.get_doc("PineLabs Order", order_id).refresh_order_details()


@frappe.whitelist()
def cancel_order(order_id):
    return frappe.get_doc("PineLabs Order", order_id).cancel_order()


def parse_reference_invoices(
    reference_invoices: list[dict],
    currency: str,
    customer_id: str | None = None,
):
    amount = 0
    company = None
    parsed_invoices = []

    for invoice in reference_invoices:
        invoice_type = invoice.get("invoice_type", "")
        invoice_id = invoice.get("invoice_id", "")
        invoice_doc = frappe.get_doc(invoice_type, invoice_id)
        if invoice_doc.docstatus != 1:
            frappe.throw(f"Invoice {invoice_type}:{invoice_id} is not submitted.")
        if invoice_doc.status == "Paid":
            frappe.throw("Invoice is already paid.")

        invoice_customer = utils.get_or_throw(invoice_doc, "customer")
        invoice_currency = utils.get_or_throw(invoice_doc, "currency")
        invoice_amount = utils.get_or_throw(invoice_doc, "grand_total")
        invoice_company = utils.get_or_throw(invoice_doc, "company")

        amount += invoice_amount
        if not customer_id:
            customer_id = invoice_customer
        if not currency:
            currency = invoice_currency
        if not company:
            company = invoice_company

        if customer_id != invoice_customer:
            frappe.throw("Customer doesn't matches across invoices.")
        if currency != invoice_currency:
            frappe.throw("Currency doesn't matches across invoices.")
        if company != invoice_company:
            frappe.throw("Company doesn't matches across invoices.")

        parsed_invoices.append({"invoice_type": invoice_type, "invoice": invoice_id})

    return {
        "currency": currency,
        "amount": amount,
        "customer": customer_id,
        "invoices": parsed_invoices,
        "company": company,
    }
