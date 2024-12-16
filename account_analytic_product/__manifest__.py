# Copyright 2024 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Account Analytic Product",
    "summary": """Shows product field on the Journal Entry""",
    "version": "16.0.1.0.0",
    "category": "Analytic Accounting",
    "license": "AGPL-3",
    "author": "Miquel Pascual, Bernat Obrador, Odoo Community Association (OCA",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account", "analytic"],
    "data": [
        "views/account_move.xml",
    ],
    "installable": True,
}
