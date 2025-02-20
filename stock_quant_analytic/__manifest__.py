# Copyright (C) 2024 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Inventory Analytic",
    "summary": """
        Allows to define the analytic account on inventory adjustments""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "depends": [
        "stock_analytic",
    ],
    "data": [
        "views/stock_quant_views.xml",
    ],
}
