from types import SimpleNamespace

import frappe
from frappe.tests.utils import FrappeTestCase

from atlas_billing.utils import validate_generic_item


class TestValidateGenericItem(FrappeTestCase):
	def test_throws_when_price_not_set(self):
		item_falso = frappe._dict(
			{
				"item_code": "SERV-GENERICO",
				"item_name": "Servicio genérico",
				"rate": 1,
				"description": "Otro servicio",
				"idx": 1,
			}
		)

		doc_falso = SimpleNamespace(items=[item_falso])

		with self.assertRaises(frappe.ValidationError):
			validate_generic_item(doc_falso, "validate")

	def test_throws_when_descrption_not_set(self):
		item_falso = frappe._dict(
			{
				"item_code": "SERV-GENERICO",
				"item_name": "Servicio genérico",
				"rate": 200,
				"idx": 1,
			}
		)
		doc_falso = SimpleNamespace(items=[item_falso])
		with self.assertRaises(frappe.ValidationError):
			validate_generic_item(doc_falso, "validate")

	def test_passes_with_description_and_price(self):
		item_falso = frappe._dict(
			{
				"item_code": "SERV-GENERICO",
				"item_name": "Servicio genérico",
				"rate": 200,
				"description": "Retoque",
				"idx": 1,
			}
		)
		doc_falso = SimpleNamespace(items=[item_falso])

		validate_generic_item(doc_falso, "validate")

	def test_passes_with_non_generic_item_no_description(self):
		item_falso = frappe._dict(
			{
				"item_code": "Non-G",
				"item_name": "Shampoo",
				"rate": 1,
				"idx": 1,
			}
		)
		doc_falso = SimpleNamespace(items=[item_falso])

		validate_generic_item(doc_falso, "validate")

	def test_passes_with_non_generic_item_description(self):
		item_falso = frappe._dict(
			{
				"item_code": "Non-G",
				"item_name": "Corte",
				"description": "Corte",
				"rate": 200,
				"idx": 1,
			}
		)
		doc_falso = SimpleNamespace(items=[item_falso])

		validate_generic_item(doc_falso, "validate")
