# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "Analytic plans per product",
    "summary": "Configure applicability of an analytic plan per product",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "maintainers": ["hbrunn"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "preloadable": True,
    "depends": [
        "account",
    ],
    "data": [
        "views/account_analytic_plan.xml",
    ],
    "demo": [
        "demo/account_analytic_plan.xml",
    ],
}
