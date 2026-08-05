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
    create_item_atributes()

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
        

        