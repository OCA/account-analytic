# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Activity Based Cost",
    "version": "14.0.2.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": "Assign overhead costs to activities, using Analytic Items",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["account"],
    "category": "Accounting/Accounting",
    "data": [
        "security/ir.model.access.csv",
        "views/activity_cost_rule_views.xml",
        "views/account_analytic_line.xml",
        "views/product_template.xml",
    ],
    "demo": [
        "demo/product_demo.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["dreispt"],
    "installable": True,
}
