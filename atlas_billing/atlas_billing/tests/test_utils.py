from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import nowdate
from frappe.utils.nestedset import get_ancestors_of, get_root_of

from atlas_billing.install import create_exempt_item_tax_template
from atlas_billing.item_events import validate_service_stock
from atlas_billing.utils import (
	validate_cancellation_reason,
	validate_closing_entry_differences,
	validate_generic_item,
	validate_locked_price,
)


def get_company():
	name = frappe.defaults.get_global_default("company") or frappe.db.get_value("Company", {}, "name")
	return frappe.get_doc("Company", name)


def get_accounting_defaults():
	"""Company, accounts and warehouse of whatever site the tests run on (dev site or CI)."""
	company = get_company()
	return frappe._dict(
		company=company.name,
		abbr=company.abbr,
		income_account=company.default_income_account or f"Sales - {company.abbr}",
		cost_center=company.cost_center or f"Main - {company.abbr}",
		warehouse=f"Stores - {company.abbr}",
	)


def get_test_customer():
	existing = frappe.db.get_value("Customer", {"customer_name": "Test Customer"})
	if existing:
		return existing

	customer = frappe.get_doc(
		{
			"doctype": "Customer",
			"customer_name": "Test Customer",
			"customer_group": get_root_of("Customer Group"),
			"territory": get_root_of("Territory"),
			"tipo_cliente": "Normal",
		}
	)
	customer.insert()
	return customer.name


def get_test_supplier():
	existing = frappe.db.get_value("Supplier", {"supplier_name": "Test Supplier"})
	if existing:
		return existing

	supplier = frappe.get_doc(
		{
			"doctype": "Supplier",
			"supplier_name": "Test Supplier",
			"supplier_group": get_root_of("Supplier Group"),
		}
	)
	supplier.insert()
	return supplier.name


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
		fake_doc = frappe._dict({"item_group": "Services", "is_stock_item": 0})
		with patch("atlas_billing.item_events.is_service_item_group", return_value=True):
			validate_service_stock(fake_doc, "validate")

	def test_fails_when_stock_is_1(self):
		fake_doc = frappe._dict({"item_group": "Services", "is_stock_item": 1})
		with patch("atlas_billing.item_events.is_service_item_group", return_value=True):
			with self.assertRaises(frappe.ValidationError):
				validate_service_stock(fake_doc, "validate")

	def test_passes_when_not_a_service(self):
		fake_doc = frappe._dict({"item_group": "Products", "is_stock_item": 1})
		with patch("atlas_billing.item_events.is_service_item_group", return_value=False):
			validate_service_stock(fake_doc, "validate")


from frappe.desk.query_report import run


class TestSalesByCategoryReport(FrappeTestCase):
	def test_splits_totals_between_service_and_product(self):
		# Today's date, so it always falls inside the fiscal year the test site has.
		test_date = nowdate()
		defaults = get_accounting_defaults()

		service_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-SERVICE-REPORT",
				"item_name": "Test Service",
				"item_group": "Services",
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

		direct_service_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-DIRECT-SERVICE-REPORT",
				"item_name": "Test Direct Service",
				"item_group": "Services",
				"stock_uom": "Nos",
				"is_stock_item": 0,
			}
		).insert()

		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": get_test_customer(),
				"company": defaults.company,
				"posting_date": test_date,
				"due_date": test_date,
				"set_posting_time": 1,
				"items": [
					{
						"item_code": service_item.name,
						"qty": 1,
						"rate": 300,
						"income_account": defaults.income_account,
						"cost_center": defaults.cost_center,
					},
					{
						"item_code": product_item.name,
						"qty": 1,
						"rate": 500,
						"income_account": defaults.income_account,
						"cost_center": defaults.cost_center,
					},
					{
						"item_code": direct_service_item.name,
						"qty": 1,
						"rate": 100,
						"income_account": defaults.income_account,
						"cost_center": defaults.cost_center,
					},
				],
			}
		)
		invoice.insert()
		invoice.submit()

		result = run(report_name="Sales by category", filters={"from_date": test_date, "to_date": test_date})

		totals = {row["categoria"]: row["total_vendido"] for row in result["result"]}

		self.assertEqual(totals.get("Servicio (Exento)"), 400)
		self.assertEqual(totals.get("Producto (Gravado)"), 500)


class TestProfitAndCostReport(FrappeTestCase):
	def test_calculates_profit(self):
		test_date = nowdate()
		defaults = get_accounting_defaults()

		service_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-SERVICE-REPORT",
				"item_name": "Test Service",
				"item_group": "Services",
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
				"is_stock_item": 1,
			}
		).insert()

		stock_entry = frappe.get_doc(
			{
				"doctype": "Purchase Receipt",
				"items": [
					{
						"item_code": product_item.name,
						"qty": 10,
						"rate": "200",
						"warehouse": defaults.warehouse,
					}
				],
				"supplier": get_test_supplier(),
				"company": defaults.company,
			}
		)
		stock_entry.insert()
		stock_entry.submit()
		invoice = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"customer": get_test_customer(),
				"company": defaults.company,
				"posting_date": test_date,
				"due_date": test_date,
				"set_posting_time": 1,
				"items": [
					{
						"item_code": product_item.name,
						"qty": 4,
						"rate": 500,
						"income_account": defaults.income_account,
						"cost_center": defaults.cost_center,
					},
					{
						"item_code": service_item.name,
						"qty": 2,
						"rate": 500,
						"income_account": defaults.income_account,
						"cost_center": defaults.cost_center,
					},
				],
			}
		)
		invoice.insert()
		invoice.submit()

		result = run(report_name="Profit and cost", filters={"from_date": test_date, "to_date": test_date})
		totals = {row["item"]: row for row in result["result"]}

		self.assertIn(product_item.name, totals)
		self.assertNotIn(service_item.name, totals)
		self.assertEqual(totals[product_item.name]["ganancia"], 1200)
		self.assertEqual(totals[product_item.name]["costo_promedio_ponderado"], 200)
		self.assertEqual(totals[product_item.name]["total_vendido"], 2000)


class TestServiceWithTaxExemption(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# The "ITBIS Exento" template is only created when an "ITBIS" account exists
		# (see install.py), and a fresh test site doesn't have one.
		defaults = get_accounting_defaults()
		if not frappe.db.exists("Account", {"account_name": "ITBIS", "company": defaults.company}):
			frappe.get_doc(
				{
					"doctype": "Account",
					"account_name": "ITBIS",
					"company": defaults.company,
					"parent_account": f"Duties and Taxes - {defaults.abbr}",
					"account_type": "Tax",
				}
			).insert()
		create_exempt_item_tax_template()

	def test_exempt_when_is_subservice(self):
		fake_service_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-XX1",
				"item_name": "Armonizacion",
				"stock_uom": "Nos",
				"item_group": "Services",
				"is_stock_item": 0,
			}
		)
		with patch("atlas_billing.item_events.is_service_item_group", return_value=True):
			fake_service_item.insert()
		self.assertEqual(len(fake_service_item.taxes), 1)
		item_tax_template = frappe.get_doc("Item Tax Template", fake_service_item.taxes[0].item_tax_template)
		self.assertEqual(item_tax_template.title, "ITBIS Exento")
		self.assertEqual(item_tax_template.taxes[0].tax_rate, 0)

	def test_exempt_when_is_service_directly(self):
		fake_service_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-XX2",
				"item_name": "Armonizacion",
				"stock_uom": "Nos",
				"item_group": "Services",
				"is_stock_item": 0,
			}
		)
		with patch("atlas_billing.item_events.is_service_item_group", return_value=True):
			fake_service_item.insert()
		self.assertEqual(len(fake_service_item.taxes), 1)
		item_tax_template = frappe.get_doc("Item Tax Template", fake_service_item.taxes[0].item_tax_template)
		self.assertEqual(item_tax_template.title, "ITBIS Exento")
		self.assertEqual(item_tax_template.taxes[0].tax_rate, 0)

	def test_fails_when_item_is_product(self):
		fake_product_item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": "TEST-XX3",
				"item_name": "Cera",
				"stock_uom": "Nos",
				"item_group": "Products",
				"is_stock_item": 1,
			}
		)
		with patch("atlas_billing.item_events.is_service_item_group", return_value=False):
			fake_product_item.insert()
		self.assertEqual(len(fake_product_item.taxes), 0)
