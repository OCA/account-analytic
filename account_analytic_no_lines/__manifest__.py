# Copyright 2016-2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic No Lines",
    "summary": """
        Hide analytics lines and disable
        their generation from a move line.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account"],
    "data": [
        "security/data_account_analytic_group.xml",
        "views/account_analytic_account.xml",
        "views/account_move_line.xml",
        "views/account_analytic.xml",
    ],
}
