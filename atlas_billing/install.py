import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields



def after_install():
    create_custom_fields({
        "Customer":[
            {   "fieldname": "tipo_cliente",
    "label": "Tipo de Cliente",
    "fieldtype": "Select",
    "options": "Normal\nVIP",
    "reqd":1,
    "insert_after": "customer_name"},
            {   "fieldname": "fecha_nacimiento",
    "label": "Fecha de Nacimiento",
    "fieldtype": "Date",
   
    "insert_after": "tipo_cliente"}
        ]
    })
    create_item_groups()
    create_item_attributes()
    create_custom()
    create_generic_item()

def create_item_groups():
        
        #Child 1 capilar 
        frappe.get_doc({
            "doctype": "Item Group",
    "item_group_name": "Capilar",
    "parent_item_group": "Services",
    "is_group": 0
        }).insert()
      #Child 2 Cuidado facial 
        frappe.get_doc({
            "doctype": "Item Group",
    "item_group_name": "Cuidado facial",
    "parent_item_group": "Services",
    "is_group": 0
        }).insert()
        #Child 3 Masaje 
        frappe.get_doc({
            "doctype": "Item Group",
    "item_group_name": "Masaje",
    "parent_item_group": "Services",
    "is_group": 0
        }).insert()
      

        
def create_item_attributes():
    frappe.get_doc({
    "doctype": "Item Attribute",
    "attribute_name": "Longitud de pelo",
    "item_attribute_values": [
        {"attribute_value": "Corto", "abbr": "S"},
        {"attribute_value": "Largo", "abbr": "L"},
        {"attribute_value": "Extra Largo", "abbr": "XL"}
    ]
    }).insert()
        

 



GENERIC_ITEM_CODE = "SERV-GENERICO"
PRICE_LIST = "Standard Selling"  # confirma que tu POS Profile usa esta

def create_generic_item():
    if not frappe.db.exists("Item", GENERIC_ITEM_CODE):
        item = frappe.get_doc({
            "doctype": "Item",
            "item_code": GENERIC_ITEM_CODE,
            "item_name": "Servicio genérico",
            "item_group": "Services",
            "is_stock_item": 0,
            "standard_rate": 0,
        })
        item.insert(ignore_permissions=True)

    if not frappe.db.exists("Item Price", {"item_code": GENERIC_ITEM_CODE, "price_list": PRICE_LIST}):
        frappe.get_doc({
            "doctype": "Item Price",
            "item_code": GENERIC_ITEM_CODE,
            "price_list": PRICE_LIST,
            "price_list_rate": 1,
        }).insert(ignore_permissions=True)

    frappe.db.commit()