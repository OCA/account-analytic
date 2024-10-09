# Copyright 2024 (APSL - Nagarro) Miquel Pascual, Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Account Analytic Document Date",
    "summary": "Account Analytic Document Date",
    "version": "16.0.1.0.0",
    "website": "https://github.com/OCA/account-analytic",
    "author": (
        "(Nagarro - APSL), Miquel Pascual, Bernat Obrador,"
        "Odoo Community Association (OCA)"
    ),
    "maintainers": ["mpascual@apsl.net, bobrador@apsl.net"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["account", "account_reconcile_oca"],
    "data": [
        "views/account_analytic_line_views.xml",
        "views/account_bank_statement_line_views.xml",
        "views/account_move.xml",
    ],
    "post_init_hook": "post_init_hook",
}
