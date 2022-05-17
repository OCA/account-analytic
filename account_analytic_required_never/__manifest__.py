# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Analytic Required Never",
    "summary": """
        This module will remove the value of analytic account in account move
        creation when analytic account policy on the account is 'Never'""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "account_analytic_required",
    ],
}
