# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Analytic Required",
    "summary": """
        This module introduces a constraint on Purchase Order form that
        requires the analytic account to be filled in.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "maintainers": ["rousseldenis"],
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "purchase_analytic",
    ],
    "data": [
        "views/purchase_order.xml",
    ],
}
