frappe.require("point-of-sale.bundle.js", function () {
	const original = erpnext.PointOfSale.ItemCart.prototype.update_customer_section;

	erpnext.PointOfSale.ItemCart.prototype.update_customer_section = function () {
		original.call(this);

		const me = this;
		const customer = me.customer_info && me.customer_info.customer;
		if (!customer) return;

		frappe.call({
			method: "atlas_billing.utils.get_customer_outstanding",
			args: { customer: customer },
			callback: function (r) {
				if (!me.customer_info || me.customer_info.customer !== customer) return;
				if (typeof r.message !== "number") return;

				const amount = flt(r.message, 2);
				let color, label;
				if (amount > 0) {
					color = "red";
					label = __("Debe {0}", [format_currency(amount)]);
				} else if (amount < 0) {
					color = "blue";
					label = __("Saldo a favor {0}", [format_currency(Math.abs(amount))]);
				} else {
					color = "green";
					label = __("Al día");
				}

				me.$customer_section.find(".atlas-outstanding").remove();
				me.$customer_section
					.find(".customer-name-desc")
					.append(
						`<span class="indicator-pill ${color} atlas-outstanding">${label}</span>`
					);
			},
		});
	};
});
