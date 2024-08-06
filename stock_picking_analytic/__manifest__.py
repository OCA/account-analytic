# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Analytic",
    "summary": """
        Allows to define the analytic account on picking level""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "stock_analytic",
        "base_view_inheritance_extension",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
}
