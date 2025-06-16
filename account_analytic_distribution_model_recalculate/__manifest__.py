# Copyright 2024 (APSL-Nagarro) - Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic Distribution Model Recalculate",
    "summary": """Add the posibility to change the analytic distribution of the journal
    items assigned by the distribution model""",
    "version": "17.0.1.0.1",
    "license": "AGPL-3",
    "author": "Odoo Community Association (OCA), APSL-Nagarro, Bernat Obrador",
    "website": "https://github.com/OCA/account-analytic",
    "maintainers": ["BernatObrador"],
    "depends": [
        "account",
        "analytic",
    ],
    "data": [
        "views/account_analytic_distribution_model.xml",
        "views/account_move_line.xml",
    ],
    "installable": True,
    "application": False,
}
