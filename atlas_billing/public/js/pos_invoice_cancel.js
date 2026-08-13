frappe.ui.form.on("POS Invoice", {
	before_cancel(frm) {
		console.log("Se debe llenar el motivo");
	},
});
