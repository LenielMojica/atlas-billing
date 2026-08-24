import frappe
from frappe import _
from frappe.utils.nestedset import get_ancestors_of


@frappe.whitelist(allow_guest=False)
def get_item_category(item_group):
	is_service = "Services" in get_ancestors_of("Item Group", item_group) or item_group == "Services"
	is_capilar_service = (
		"Servicios capilares" in get_ancestors_of("Item Group", item_group)
		or item_group == "Servicios capilares"
	)

	return {"is_capilar": is_capilar_service, "is_service": is_service}


# Create variants automatically for capilar services for length of hair
def create_hair_variants(doc, method):
	is_capilar_service = (
		"Servicios capilares" in get_ancestors_of("Item Group", doc.item_group)
		or doc.item_group == "Servicios capilares"
	)
	if is_capilar_service and not doc.variant_of:
		frappe.db.set_value("Item", doc.name, "has_variants", 1)

		frappe.get_doc(
			{
				"doctype": "Item Variant Attribute",
				"parent": doc.name,
				"parenttype": "Item",
				"parentfield": "attributes",
				"attribute": "Longitud de pelo",
			}
		).insert()

		attribute = frappe.get_doc("Item Attribute", "Longitud de pelo")

		for value in attribute.item_attribute_values:
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": doc.item_code + "-" + value.abbr,
					"item_group": doc.item_group,
					"variant_of": doc.item_code,
					"item_name": doc.item_name + "-" + value.attribute_value,
					"is_stock_item": 0,
					"stock_uom": "Nos",
					"attributes": [
						{"attribute": "Longitud de pelo", "attribute_value": value.attribute_value}
					],
				}
			).insert()


def validate_service_stock(doc, method):
	is_service = "Services" in get_ancestors_of("Item Group", doc.item_group) or doc.item_group == "Services"

	if (is_service) and doc.is_stock_item:
		frappe.throw(_("Los servicios no deben mantener inventario"))


def validate_service_tax_exemption(doc, method):
	is_service = "Services" in get_ancestors_of("Item Group", doc.item_group) or doc.item_group == "Services"
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
