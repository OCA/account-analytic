# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Analytic Accounting support for WIP and Variances",
    "version": "14.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": "Track and report WIP and Variances based on Analytic Items",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["stock_account"],
    "category": "Accounting/Accounting",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/activity_cost_rule_views.xml",
        "views/product_category.xml",
        "views/product_template.xml",
        "views/account_move.xml",
        "views/account_analytic_line.xml",
        "views/account_analytic_tracking.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["dreispt"],
    "installable": True,
}
