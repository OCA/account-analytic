# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account move analytic link",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "This module allows users to navigate from journal items that "
    "have analytic distribution assigned to the analytic items generated.",
    "author": "ForgeFlow,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "views/account_move_line_views.xml",
    ],
    "installable": True,
    "application": False,
}
