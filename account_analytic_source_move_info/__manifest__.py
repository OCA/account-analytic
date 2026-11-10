# Copyright 2026 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Analytic Source Move Info",
    "summary": "Show move base amounts and analytic percentage on analytic items",
    "version": "17.0.1.0.0",
    "category": "Accounting/Accounting",
    "website": "https://github.com/OCA/account-analytic",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["BernatObrador"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account",
        "analytic",
    ],
    "data": [
        "views/account_analytic_line_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
}
