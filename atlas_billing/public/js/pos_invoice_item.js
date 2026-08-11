const GENERIC_ITEM_CODE = "SERV-GENERICO";

frappe.ui.form.on("POS Invoice Item", {
    item_code(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.item_code !== GENERIC_ITEM_CODE) return;

       

frappe.ui.form.on("POS Invoice Item", {
    item_code(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        if (row.item_code !== GENERIC_ITEM_CODE) return;

        const dialog = new frappe.ui.Dialog({
            title: "Describe el servicio genérico",
            static: true,
            fields: [
                {
                    fieldname: "description",
                    label: "¿Qué servicio se realizó?",
                    fieldtype: "Small Text",
                    reqd: 1,
                },
            ],
            primary_action_label: "Guardar",
            primary_action(values) {
                frappe.model.set_value(cdt, cdn, "description", values.description);
                dialog.hide();
            },
        });

        dialog.show();
    }
});
    }
});