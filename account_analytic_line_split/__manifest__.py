# Copyright 2024 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic Line Split",
    "summary": """
        Account Analytic Line Split""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["account", "analytic"],
    "data": [
        "views/account_analytic_line.xml",
        "views/account_move.xml",
        "wizard/analytic_line_split_wizard.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
}
