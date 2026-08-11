import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


# Create variants automatically for capilar services for length of hair
def create_hair_variants(doc, method):
	if doc.item_group == "Capilar" and not doc.variant_of:
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
