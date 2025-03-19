# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account analytic distribution manual",
    "summary": "Account analytic distribution manual",
    "version": "17.0.1.0.1",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "depends": ["account"],
    "data": [
        "security/analytic_security.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_distribution_manual_views.xml",
        "views/account_analytic_line_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_analytic_distribution_manual/static/src/components/**/*",
        ],
        "web.assets_tests": [
            "account_analytic_distribution_manual/static/src/tests/tours/**/*",
        ],
    },
    "installable": True,
}
