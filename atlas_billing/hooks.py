app_name = "atlas_billing"
app_title = "atlas-biling"
app_publisher = "Leniel"
app_description = "Billing app"
app_email = "lenielmr@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "atlas_billing",
# 		"logo": "/assets/atlas_billing/logo.png",
# 		"title": "atlas-biling",
# 		"route": "/atlas_billing",
# 		"has_permission": "atlas_billing.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------
fixtures = [
	{
		"dt": "Custom Field",
		"filters": [
			[
				"fieldname",
				"in",
				["cancellation_reason", "tipo_cliente", "fecha_nacimiento", "custom_motivo_de_la_diferencia"],
			]
		],
	},
	{"dt": "Item Group", "filters": [["name", "in", ["Capilar", "Cuidado facial", "Masaje"]]]},
	{"dt": "Item Attribute", "filters": [["name", "=", "Longitud de pelo"]]},
	{"dt": "Property Setter", "filters": [["name", "=", "Journal Entry-user_remark-reqd"]]},
	{"dt": "Report", "filters": [["name", "in", ["Profit and cost", "Sales by category"]]]},
	{"dt": "Print Format", "filters": [["name", "=", "Los gladiolos"]]},
	{"dt": "Print Settings"},
	{"dt": "Role", "filters": [["name", "in", ["Cajera", "Gerente"]]]},
]

doctype_js = {
	"POS Invoice": ["public/js/pos_invoice_item.js", "public/js/pos_invoice_cancel.js"],
	"Item": ["public/js/item_variants_handler.js"],
}
# include js, css files in header of desk.html
# app_include_css = "/assets/atlas_billing/css/atlas_billing.css"
# app_include_js = "/assets/atlas_billing/js/atlas_billing.js"

# include js, css files in header of web template
# web_include_css = "/assets/atlas_billing/css/atlas_billing.css"
# web_include_js = "/assets/atlas_billing/js/atlas_billing.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "atlas_billing/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "atlas_billing/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "atlas_billing.utils.jinja_methods",
# 	"filters": "atlas_billing.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "atlas_billing.install.before_install"
# after_install = "atlas_billing.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "atlas_billing.uninstall.before_uninstall"
# after_uninstall = "atlas_billing.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "atlas_billing.utils.before_app_install"
# after_app_install = "atlas_billing.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "atlas_billing.utils.before_app_uninstall"
# after_app_uninstall = "atlas_billing.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "atlas_billing.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Item": {
		# 		"on_update": "method",
		# 		"on_cancel": "method",
		# 		"on_trash": "method"
		"after_insert": "atlas_billing.item_events.create_hair_variants",
		"validate": [
			"atlas_billing.item_events.validate_service_stock",
			"atlas_billing.item_events.validate_service_tax_exemption",
		],
	},
	"POS Invoice": {
		"validate": [
			"atlas_billing.utils.validate_generic_item",
			"atlas_billing.utils.validate_locked_price",
		],
		"before_cancel": "atlas_billing.utils.validate_cancellation_reason",
	},
	"POS Closing Entry": {
		"validate": "atlas_billing.utils.validate_closing_entry_differences",
	},
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"atlas_billing.tasks.all"
# 	],
# 	"daily": [
# 		"atlas_billing.tasks.daily"
# 	],
# 	"hourly": [
# 		"atlas_billing.tasks.hourly"
# 	],
# 	"weekly": [
# 		"atlas_billing.tasks.weekly"
# 	],
# 	"monthly": [
# 		"atlas_billing.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "atlas_billing.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "atlas_billing.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "atlas_billing.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["atlas_billing.utils.before_request"]
# after_request = ["atlas_billing.utils.after_request"]

# Job Events
# ----------
# before_job = ["atlas_billing.utils.before_job"]
# after_job = ["atlas_billing.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"atlas_billing.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

after_install = "atlas_billing.install.after_install"
