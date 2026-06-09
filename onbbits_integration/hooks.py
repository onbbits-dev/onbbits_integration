app_name = "onbbits_integration"
app_title = "Onbbits Integration"
app_publisher = "It provides complete, centralized control over WhatsApp communication inside Frappe, enabling businesses to automate customer messaging with accuracy, reliability, and real-time synchronization."
app_description = "The OnBBits Integration App is a Frappe-based extension designed to seamlessly connect your ERP system with the OnBBits WhatsApp Messaging Platform."
app_email = "krishna@arkayapps.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "onbbits_integration",
# 		"logo": "/assets/onbbits_integration/logo.png",
# 		"title": "Onbbits Integration",
# 		"route": "/onbbits_integration",
# 		"has_permission": "onbbits_integration.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/onbbits_integration/css/onbbits_integration.css"
# app_include_js = "/assets/onbbits_integration/js/onbbits_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/onbbits_integration/css/onbbits_integration.css"
# web_include_js = "/assets/onbbits_integration/js/onbbits_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "onbbits_integration/public/scss/website"

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
# app_include_icons = "onbbits_integration/public/icons.svg"

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
# 	"methods": "onbbits_integration.utils.jinja_methods",
# 	"filters": "onbbits_integration.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "onbbits_integration.install.before_install"
# after_install = "onbbits_integration.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "onbbits_integration.uninstall.before_uninstall"
# after_uninstall = "onbbits_integration.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "onbbits_integration.utils.before_app_install"
# after_app_install = "onbbits_integration.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "onbbits_integration.utils.before_app_uninstall"
# after_app_uninstall = "onbbits_integration.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "onbbits_integration.notifications.get_notification_config"

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
	"*": {
        "before_insert":
            "onbbits_integration.api.validate_onbbits_event",
        "on_update":
            "onbbits_integration.api.validate_onbbits_event",
        "on_submit":
            "onbbits_integration.api.validate_onbbits_event",
        "on_cancel":
            "onbbits_integration.api.validate_onbbits_event",
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"onbbits_integration.tasks.all"
# 	],
# 	"daily": [
# 		"onbbits_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"onbbits_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"onbbits_integration.tasks.weekly"
# 	],
# 	"monthly": [
# 		"onbbits_integration.tasks.monthly"
# 	],
    "hourly": [
        "onbbits_integration.onbbits_api.sync_template_status"
    ]
}

# Testing
# -------

# before_tests = "onbbits_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "onbbits_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "onbbits_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["onbbits_integration.utils.before_request"]
# after_request = ["onbbits_integration.utils.after_request"]

# Job Events
# ----------
# before_job = ["onbbits_integration.utils.before_job"]
# after_job = ["onbbits_integration.utils.after_job"]

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
# 	"onbbits_integration.auth.validate"
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

fixtures = [
    "Template Language", "Template Category",
    {"dt": "Client Script", "filters": [["name", "=", "ONBBITS"]]}, 
    {"dt": "Workspace", "filters": [["name", "=", "ONBBITS"]]}, 
    {"dt": "Property Setter","filters": [["module", "=", "Onbbits Integration"]]}
]

