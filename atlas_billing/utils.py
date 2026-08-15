import frappe
from frappe import _

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
