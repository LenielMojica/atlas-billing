frappe.ui.form.on("POS Invoice", {
	before_cancel(frm) {
		return new Promise((resolve, reject) => {
			new frappe.ui.Dialog({
				title: "Por que cancelas?",
				fields: [
					{
						fieldname: "reason",
						label: "Motivo",
						fieldtype: "Small Text",
						reqd: 1,
					},
				],
				static: true,
				primary_action_label: "Confirmar",
				primary_action(value) {
					frm.set_value("cancellation_reason", value.reason);
					frm.save("Update").then(() => {
						this.hide();
						resolve();
					});
				},
			}).show();
		});
	},
});
