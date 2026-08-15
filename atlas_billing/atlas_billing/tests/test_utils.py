from types import SimpleNamespace

import frappe
from frappe.tests.utils import FrappeTestCase

from atlas_billing.utils import (
	validate_cancellation_reason,
	validate_closing_entry_differences,
	validate_generic_item,
)


class TestValidateGenericItem(FrappeTestCase):
	def test_throws_when_price_not_set(self):
		fake_item = frappe._dict(
			{
				"item_code": "SERV-GENERICO",
				"item_name": "Servicio genérico",
				"rate": 1,
				"description": "Otro servicio",
				"idx": 1,
			}
		)

		fake_doc = SimpleNamespace(items=[fake_item])

		with self.assertRaises(frappe.ValidationError):
			validate_generic_item(fake_doc, "validate")

	def test_throws_when_descrption_not_set(self):
		fake_item = frappe._dict(
			{
				"item_code": "SERV-GENERICO",
				"item_name": "Servicio genérico",
				"rate": 200,
				"idx": 1,
			}
		)
		fake_doc = SimpleNamespace(items=[fake_item])
		with self.assertRaises(frappe.ValidationError):
			validate_generic_item(fake_doc, "validate")

	def test_passes_with_description_and_price(self):
		fake_item = frappe._dict(
			{
				"item_code": "SERV-GENERICO",
				"item_name": "Servicio genérico",
				"rate": 200,
				"description": "Retoque",
				"idx": 1,
			}
		)
		fake_doc = SimpleNamespace(items=[fake_item])

		validate_generic_item(fake_doc, "validate")

	def test_passes_with_non_generic_item_no_description(self):
		fake_item = frappe._dict(
			{
				"item_code": "Non-G",
				"item_name": "Shampoo",
				"rate": 1,
				"idx": 1,
			}
		)
		fake_doc = SimpleNamespace(items=[fake_item])

		validate_generic_item(fake_doc, "validate")

	def test_passes_with_non_generic_item_description(self):
		fake_item = frappe._dict(
			{
				"item_code": "Non-G",
				"item_name": "Corte",
				"description": "Corte",
				"rate": 200,
				"idx": 1,
			}
		)
		fake_doc = SimpleNamespace(items=[fake_item])

		validate_generic_item(fake_doc, "validate")


class TestValidateCancellationReason(FrappeTestCase):
	def test_description_throws_when_none(self):
		fake_inv = SimpleNamespace(cancellation_reason=None)

		with self.assertRaises(frappe.ValidationError):
			validate_cancellation_reason(fake_inv, "before_cancellation")

	def test_description_throws_when_set_to_spaces(self):
		fake_inv = SimpleNamespace(cancellation_reason="      ")

		with self.assertRaises(frappe.ValidationError):
			validate_cancellation_reason(fake_inv, "before_cancellation")

	def test_description_throws_when_set_empty(self):
		fake_inv = SimpleNamespace(cancellation_reason="")

		with self.assertRaises(frappe.ValidationError):
			validate_cancellation_reason(fake_inv, "before_cancel")


class TestValidateDifferenceReason(FrappeTestCase):
	def test_difference_reason_throws_when_empty(self):
		fake_row = frappe._dict(
			{
				"mode_of_payment": "Cash",
				"difference": 400,
				"custom_motivo_de_la_diferencia": "",
			}
		)
		fake_doc = SimpleNamespace(payment_reconciliation=[fake_row])

		with self.assertRaises(frappe.ValidationError):
			validate_closing_entry_differences(fake_doc, "validate")

	def test_passes_when_difference_and_reason_given(self):
		fake_row = frappe._dict(
			{
				"mode_of_payment": "Cash",
				"difference": 400,
				"custom_motivo_de_la_diferencia": "Se cobró de más por error",
			}
		)
		fake_doc = SimpleNamespace(payment_reconciliation=[fake_row])
		validate_closing_entry_differences(fake_doc, "validate")

	def test_passes_when_no_difference(self):
		fake_row = frappe._dict(
			{
				"mode_of_payment": "Cash",
				"difference": 0,
				"custom_motivo_de_la_diferencia": "",
			}
		)
		fake_doc = SimpleNamespace(payment_reconciliation=[fake_row])

		validate_closing_entry_differences(fake_doc, "validate")
