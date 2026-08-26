import frappe


def after_install():
	create_exempt_item_tax_template()
	create_generic_item()


GENERIC_ITEM_CODE = "SERV-GENERICO"
PRICE_LIST = "Standard Selling"  # confirma que tu POS Profile usa esta


def create_generic_item():
	if not frappe.db.exists("Item", GENERIC_ITEM_CODE):
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": GENERIC_ITEM_CODE,
				"item_name": "Servicio genérico",
				"item_group": "Services",
				"is_stock_item": 0,
				"standard_rate": 0,
				"uom": "Nos",
			}
		)
		item.insert(ignore_permissions=True)

	if not frappe.db.exists("Item Price", {"item_code": GENERIC_ITEM_CODE, "price_list": PRICE_LIST}):
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": GENERIC_ITEM_CODE,
				"price_list": PRICE_LIST,
				"price_list_rate": 1,
			}
		).insert(ignore_permissions=True)


def create_exempt_item_tax_template():
	companies = frappe.get_all("Company", pluck="name")
	if not companies:
		return
	company = companies[0]

	account = frappe.db.get_value("Account", {"account_name": "ITBIS", "company": company})
	if not account:
		return
	if frappe.db.exists("Item Tax Template", {"title": "ITBIS Exento", "company": company}):
		return

	frappe.get_doc(
		{
			"doctype": "Item Tax Template",
			"title": "ITBIS Exento",
			"company": company,
			"taxes": [{"tax_type": account, "tax_rate": 0}],
		}
	).insert()
