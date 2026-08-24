frappe.ui.form.on("Item", {
	item_group(frm) {
		if (!frm.doc.item_group) return;
		frappe.call({
			method: "atlas_billing.item_events.get_item_category",
			args: { item_group: frm.doc.item_group },
			callback: function (r) {
				frm.set_df_property("is_stock_item", "read_only", 0);
				frm.set_value("has_variants", 0);
				if (!r.message.is_service) {
					return;
				}
				frm.set_df_property("is_stock_item", "read_only", r.message.is_service);
				frm.set_value("is_stock_item", 0);
				if (!r.message.is_capilar) {
					return;
				}
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
	},
});
