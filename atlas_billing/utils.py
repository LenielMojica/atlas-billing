import frappe
from frappe import _

from atlas_billing.install import GENERIC_ITEM_CODE


def validate_generic_item(doc, method):
	for item in doc.items:
		if item.item_code != GENERIC_ITEM_CODE:
			continue

		if item.rate <= 1 or not item.description or item.description == item.item_name:
			frappe.throw(_("Los servicios genéricos deben tener descripción y precio mayor a 1. "))
