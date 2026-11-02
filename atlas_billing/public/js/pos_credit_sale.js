frappe.require("point-of-sale.bundle.js", function () {
	const original = erpnext.PointOfSale.Payment.prototype.bind_events;
	erpnext.PointOfSale.Payment.prototype.bind_events = function () {
		original.call(this);
		this.$component.off("click", ".submit-order-btn");
		this.$component.on("click", ".submit-order-btn", () => {
			const doc = this.events.get_frm().doc;

			const items = doc.items;

			if (!this.validate_reqd_invoice_fields()) {
				return;
			}
			if (!items.length) {
				const message = __("You cannot submit empty order.");
				frappe.show_alert({ message, indicator: "orange" });
				frappe.utils.play_sound("error");
				return;
			}

			this.events.submit_invoice();
		});
	};
});
