const GENERIC_ITEM_CODE = "SERV-GENERICO";

frappe.ui.form.on("POS Invoice Item", {
	item_code(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.item_code !== GENERIC_ITEM_CODE) return;
		new frappe.ui.Dialog({
			title: "Que servicio es?",
			fields: [
				{
					label: "Description",
					fieldname: "description",
					fieldtype: "Data",
					reqd: 1,
				},
				{
					label: "Precio",
					fieldname: "rate",
					fieldtype: "Currency",
					reqd: 1,
					default: 1,
				},
			],

			static: true,
			primary_action_label: "Confirmar",
			primary_action(values) {
				if (values.rate <= 1) {
					frappe.msgprint("El precio debe ser mayor a 1");
					return;
				}
				frappe.model.set_value(cdt, cdn, "description", values.description);
				frappe.model.set_value(cdt, cdn, "rate", values.rate);

				this.hide();
			},
			secondary_action_label: "Cancelar",
			secondary_action() {
				this.hide();
			},
		}).show();
	},
});
