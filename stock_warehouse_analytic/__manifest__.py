# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Warehouse Analytic",
    "summary": """
        Allows to mention an analytic account on warehouse level""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": ["stock", "analytic"],
    "data": [
        "views/stock_warehouse.xml",
    ],
}
