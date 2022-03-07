# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Type Analytic",
    "summary": """
        Allows to define an analytic account on picking types in order to set
        it by default on pickings""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "maintainers": ["rousseldenis"],
    "depends": [
        "stock",
        "analytic",
        "stock_picking_analytic",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
}
