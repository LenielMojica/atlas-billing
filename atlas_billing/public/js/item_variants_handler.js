frappe.ui.form.on("Item", {
	item_group(frm) {
		if (!frm.doc.item_group) return;

		frappe.db
			.get_value("Item Group", frm.doc.item_group, "parent_item_group")
			.then(({ message }) => {
				const is_service = message.parent_item_group === "Services";
				frm.set_df_property("is_stock_item", "read_only", is_service);
				if (is_service) {
					frm.set_value("is_stock_item", 0);
				}
			});

		if (frm.doc.item_group !== "Capilar") return;
		frm.set_value("has_variants", 1);

		const already_has_attribute = (frm.doc.attributes || []).some(
			(row) => row.attribute === "Longitud de pelo"
		);
		if (already_has_attribute) return;

		let row = frm.add_child("attributes");
		frappe.model.set_value(row.doctype, row.name, "attribute", "Longitud de pelo");
		frm.refresh_field("attributes");
	},
});
