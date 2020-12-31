# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Activity Based Cost",
    "version": "14.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": """Analytic Activity Based Cost""",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["hr_timesheet", "account"],
    "category": "Accounting/Timesheet",
    "data": [
        "security/ir.model.access.csv",
        "views/activity_cost_rule_views.xml",
    ],
    "installable": True,
}
