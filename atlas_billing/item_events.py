import frappe
from frappe import _
from frappe.model.naming import make_autoname
from frappe.utils.nestedset import get_ancestors_of

# @frappe.whitelist(allow_guest=False)
# def get_item_category(item_group):
# is_service = "Services" in get_ancestors_of("Item Group", item_group) or item_group == "Services"
# is_capilar_service = (
# "Servicios capilares" in get_ancestors_of("Item Group", item_group)
# or item_group == "Servicios capilares"
# )

# return {"is_capilar": is_capilar_service, "is_service": is_service}


# Create variants automatically for capilar services for length of hair
# def create_hair_variants(doc, method):
# is_capilar_service = (
# "Servicios capilares" in get_ancestors_of("Item Group", doc.item_group)
# or doc.item_group == "Servicios capilares"
# )
# if is_capilar_service and not doc.variant_of:
# frappe.db.set_value("Item", doc.name, "has_variants", 1)

# frappe.get_doc(
# {
# "doctype": "Item Variant Attribute",
# "parent": doc.name,
# "parenttype": "Item",
# "parentfield": "attributes",
# "attribute": "Longitud de pelo",
# }
# ).insert()

# attribute = frappe.get_doc("Item Attribute", "Longitud de pelo")

# for value in attribute.item_attribute_values:
# frappe.get_doc(
# {
# "doctype": "Item",
# "item_code": doc.item_code + "-" + value.abbr,
# "item_group": doc.item_group,
# "variant_of": doc.item_code,
# "item_name": doc.item_name + "-" + value.attribute_value,
# "is_stock_item": 0,
# "stock_uom": "Nos",
# "attributes": [
# {"attribute": "Longitud de pelo", "attribute_value": value.attribute_value}
# ],
# }
# ).insert()


def _item_group_has_category(item_group, category):
	"""Check doc.item_group and its ancestors for a custom_item_category flag.

	custom_item_category is a Custom Field on Item Group holding a fixed value
	("Service"/"Product") set once by hand after setup. Item Group names get
	translated by ERPNext's setup wizard depending on the site's language, so
	comparing against literal names like "Services" breaks as soon as the
	wizard runs in a language other than English.
	"""
	groups = [*get_ancestors_of("Item Group", item_group), item_group]
	return bool(
		frappe.db.get_value("Item Group", {"name": ["in", groups], "custom_item_category": category}, "name")
	)


def is_service_item_group(item_group):
	return _item_group_has_category(item_group, "Service")


def is_product_item_group(item_group):
	return _item_group_has_category(item_group, "Product")


def validate_service_stock(doc, method):
	is_service = is_service_item_group(doc.item_group)

	if (is_service) and doc.is_stock_item:
		frappe.throw(_("Los servicios no deben mantener inventario"))


def validate_service_tax_exemption(doc, method):
	is_service = is_service_item_group(doc.item_group)
	if not is_service:
		return
	companies = frappe.get_all("Company", pluck="name")
	if not companies:
		return
	company = companies[0]
	tax_template = frappe.db.get_value("Item Tax Template", {"title": "ITBIS Exento", "company": company})

	for tax in doc.taxes:
		if tax.item_tax_template == tax_template:
			return
	doc.append("taxes", {"item_tax_template": tax_template})


def validate_item_tax_template(doc, method):
	is_product = is_product_item_group(doc.item_group)
	if not is_product:
		return
	companies = frappe.get_all("Company", pluck="name")
	if not companies:
		return
	company = companies[0]
	tax_template = frappe.db.get_value(
		"Item Tax Template", {"title": "Dominican Republic Tax", "company": company}
	)
	for tax in doc.taxes:
		if tax.item_tax_template == tax_template:
			return
	doc.append("taxes", {"item_tax_template": tax_template})


def assign_code(doc, method):
	item_code = ""
	ancestors_codes = []
	ancestors = get_ancestors_of("Item Group", doc.item_group)

	if not ancestors:
		return
	for i in reversed(ancestors):
		code = frappe.db.get_value("Item Group", i, "custom_group_code")
		if not code:
			continue

		ancestors_codes.append(code)

	ancestors_codes.append(frappe.db.get_value("Item Group", doc.item_group, "custom_group_code"))

	item_code = "-".join(ancestors_codes)
	doc.item_code = make_autoname(f"{item_code}-.####")
