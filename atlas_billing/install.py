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