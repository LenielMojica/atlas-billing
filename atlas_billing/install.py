import frappe


def after_install():
	create_exempt_item_tax_template()
	create_generic_item()


GENERIC_ITEM_CODE = "SERV-GENERICO"


def _get_service_item_group():
	"""Find the Item Group flagged custom_item_category="Service", creating one if none exists yet.

	Avoids hardcoding a group name: ERPNext's setup wizard names its default
	groups ("Services", "Servicios", etc.) depending on the site's language.
	"""
	existing = frappe.db.get_value("Item Group", {"custom_item_category": "Service"}, "name")
	if existing:
		return existing

	root = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ""}, "name")
	item_group = frappe.get_doc(
		{
			"doctype": "Item Group",
			"item_group_name": "Servicios",
			"parent_item_group": root,
			"is_group": 0,
			"custom_item_category": "Service",
		}
	)
	item_group.insert(ignore_permissions=True)
	return item_group.name


def create_generic_item():
	if not frappe.db.exists("Item", GENERIC_ITEM_CODE):
		item = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": GENERIC_ITEM_CODE,
				"item_name": "Servicio genérico",
				"item_group": _get_service_item_group(),
				"is_stock_item": 0,
				"standard_rate": 0,
				"uom": "Nos",
			}
		)
		item.flags.skip_auto_item_code = True
		item.insert(ignore_permissions=True)

	price_list = frappe.db.get_single_value("Selling Settings", "selling_price_list") or "Standard Selling"
	if not frappe.db.exists("Item Price", {"item_code": GENERIC_ITEM_CODE, "price_list": price_list}):
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": GENERIC_ITEM_CODE,
				"price_list": price_list,
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
