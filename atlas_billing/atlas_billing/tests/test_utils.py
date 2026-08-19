from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from atlas_billing.item_events import validate_service_stock
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


class TestValidateServiceStock(FrappeTestCase):
	def test_passes_when_stock_is_0(self):
		fake_doc = frappe._dict(
			{
				"is_stock_item": 0,
			}
		)
		with patch("atlas_billing.item_events.frappe.db.get_value", return_value="Services"):
			validate_service_stock(fake_doc, "validate")

	def test_fails_when_stock_is_1(self):
		fake_doc = frappe._dict(
			{
				"is_stock_item": 1,
			}
		)
		with patch("atlas_billing.item_events.frappe.db.get_value", return_value="Services"):
			with self.assertRaises(frappe.ValidationError):
				validate_service_stock(fake_doc, "validate")


class TestCreateHairVariants(FrappeTestCase):
	def test_creates_three_variants_for_capilar_item(self):
		parent = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-CORTE-HAIR",
				"item_name": "Test Corte",
				"item_group": "Capilar",
				"stock_uom": "Nos",
				"is_stock_item": 0,
			}
		).insert()

		variants = frappe.get_all("Item", filters={"variant_of": parent.name}, fields=["item_code"])

		self.assertEqual(len(variants), 3)
		expected_codes = {f"{parent.name}-S", f"{parent.name}-L", f"{parent.name}-XL"}
		self.assertEqual({v.item_code for v in variants}, expected_codes)


from frappe.desk.query_report import run


class TestSalesByCategoryReport(FrappeTestCase):
	def test_splits_totals_between_service_and_product(self):
		test_date = "2026-02-15"

		service_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-SERVICE-REPORT",
				"item_name": "Test Service",
				"item_group": "Cuidado facial",
				"stock_uom": "Nos",
				"is_stock_item": 0,
			}
		).insert()

		product_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-PRODUCT-REPORT",
				"item_name": "Test Product",
				"item_group": "Products",
				"stock_uom": "Nos",
				"is_stock_item": 0,
			}
		).insert()

		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": "Leniel",
				"company": "Ejemplo Src",
				"posting_date": test_date,
				"due_date": test_date,
				"set_posting_time": 1,
				"items": [
					{
						"item_code": service_item.name,
						"qty": 1,
						"rate": 300,
						"income_account": "Sales - ES",
						"cost_center": "Main - ES",
					},
					{
						"item_code": product_item.name,
						"qty": 1,
						"rate": 500,
						"income_account": "Sales - ES",
						"cost_center": "Main - ES",
					},
				],
			}
		)
		invoice.insert()
		invoice.submit()

		result = run(report_name="Sales by category", filters={"from_date": test_date, "to_date": test_date})

		totals = {row["categoria"]: row["total_vendido"] for row in result["result"]}

		self.assertEqual(totals.get("Servicio (Exento)"), 300)
		self.assertEqual(totals.get("Producto (Gravado)"), 500)
