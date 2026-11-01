import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account
from frappe import _
from frappe.utils import nowdate

from atlas_billing.install import GENERIC_ITEM_CODE


def validate_generic_item(doc, method):
	for item in doc.items:
		if item.item_code != GENERIC_ITEM_CODE:
			continue

		if item.rate <= 1 or not item.description or item.description == item.item_name:
			frappe.throw(_("Los servicios genéricos deben tener descripción y precio mayor a 1."))


def validate_cancellation_reason(doc, method):
	if not doc.cancellation_reason or not doc.cancellation_reason.strip():
		frappe.throw(_("Debe ingresar un motivo para anular la venta."))


def validate_closing_entry_differences(doc, method):
	for row in doc.payment_reconciliation:
		if row.difference and not row.custom_motivo_de_la_diferencia:
			frappe.throw(_("Hay diferencias sin detallar en {0}").format(row.mode_of_payment))


def validate_locked_price(doc, method):
	if "Item Manager" in frappe.get_roles(frappe.session.user):
		return
	for item in doc.items:
		if item.item_code == GENERIC_ITEM_CODE:
			continue
		catalog_rate = frappe.db.get_value(
			"Item Price",
			{"item_code": item.item_code, "price_list": doc.selling_price_list},
			"price_list_rate",
		)
		if catalog_rate is not None and item.rate != catalog_rate:
			frappe.throw(_("El precio de  {0} no coincide con el catalogo").format(item.item_name))


@frappe.whitelist()
def get_customer_outstanding(customer: str):
	frappe.has_permission("Customer", doc=customer, throw=True)

	sales_invoice_outstanding = frappe.get_all(
		"Sales Invoice",
		filters={"customer": customer, "docstatus": 1, "outstanding_amount": ("!=", 0)},
		pluck="outstanding_amount",
	)
	pos_invoice_outstanding = frappe.get_all(
		"POS Invoice",
		filters={
			"customer": customer,
			"docstatus": 1,
			"consolidated_invoice": ("is", "not set"),
			"outstanding_amount": ("!=", 0),
		},
		pluck="outstanding_amount",
	)
	return sum(sales_invoice_outstanding) + sum(pos_invoice_outstanding)


@frappe.whitelist()
def make_customer_payment_entry(
	customer: str, company: str | None = None, mode_of_payment: str | None = None
):
	"""Unsaved Payment Entry receiving money from `customer`, with every account and currency set."""
	frappe.has_permission("Customer", doc=customer, throw=True)
	frappe.has_permission("Payment Entry", "create", throw=True)
	company = company or frappe.defaults.get_user_default("Company")

	payment = frappe.new_doc("Payment Entry")
	payment.update(
		{
			"payment_type": "Receive",
			"company": company,
			"posting_date": nowdate(),
			"party_type": "Customer",
			"party": customer,
			"mode_of_payment": mode_of_payment,
		}
	)
	if mode_of_payment:
		payment.paid_to = get_bank_cash_account(mode_of_payment, company)["account"]
	else:
		payment.paid_to = frappe.get_cached_value("Company", company, "default_cash_account")

	# ERPNext's own helpers: customer's receivable account, names, currencies, balances, rates.
	payment.setup_party_account_field()
	payment.set_missing_values()
	payment.set_exchange_rate()
	return payment
