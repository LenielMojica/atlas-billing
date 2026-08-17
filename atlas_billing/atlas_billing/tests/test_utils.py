from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from atlas_billing.utils import (
	validate_cancellation_reason,
	validate_closing_entry_differences,
	validate_generic_item,
	validate_locked_price,
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


class TestValidateLockedPrice(FrappeTestCase):
	def test_passes_when_user_is_item_manager(self):
		fake_item = frappe._dict({"item_code": "Non-G", "item_name": "Corte-Corto", "rate": 999})
		fake_doc = SimpleNamespace(items=[fake_item], selling_price_list="Standard Selling")

		with patch("atlas_billing.utils.frappe.get_roles", return_value=["Item Manager"]):
			validate_locked_price(fake_doc, "validate")

	def test_passes_when_user_is_not_item_manager(self):
		fake_item = frappe._dict({"item_code": "Corte-001", "item_name": "Corte", "rate": 500})
		fake_doc = SimpleNamespace(items=[fake_item], selling_price_list="Standard Selling")

		with (
			patch(
				"atlas_billing.utils.frappe.get_roles",
				return_value=["Sales User", "Stock User", "Accounts User"],
			),
			patch("atlas_billing.utils.frappe.db.get_value", return_value=500),
		):
			validate_locked_price(fake_doc, "validate")

	def test_fails_when_user_is_not_item_manager(self):
		fake_item = frappe._dict({"item_code": "Corte-001", "item_name": "Corte", "rate": 500})
		fake_doc = SimpleNamespace(items=[fake_item], selling_price_list="Standard Selling")

		with (
			patch(
				"atlas_billing.utils.frappe.get_roles",
				return_value=["Sales User", "Stock User", "Accounts User"],
			),
			patch("atlas_billing.utils.frappe.db.get_value", return_value=1000),
		):
			with self.assertRaises(frappe.ValidationError):
				validate_locked_price(fake_doc, "validate")
