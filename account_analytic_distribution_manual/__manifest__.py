# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account analytic distribution manual",
    "summary": "Account analytic distribution manual",
    "version": "16.0.2.2.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "depends": ["account"],
    "data": [
        "security/analytic_security.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_distribution_manual_views.xml",
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
    "post_init_hook": "post_init_hook",
}
