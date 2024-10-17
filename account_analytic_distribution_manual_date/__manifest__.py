# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account analytic distribution manual date",
    "summary": "Account analytic distribution manual date",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/account-analytic",
    "author": "(Nagarro - APSL) Bernat Obrador, Odoo Community Association (OCA)",
    "depends": ["account_analytic_distribution_manual"],
    "data": [
        "views/account_analytic_distribution_manual_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_analytic_distribution_manual_date/static/src/components/**/*",
        ],
    },
    "installable": True,
}
