# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Quant Analytic",
    "summary": """
        Stock Quant Analytic """,
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Warehouse Management",
    "version": "15.0.0.1.0",
    "license": "AGPL-3",
    "depends": ["analytic", "stock_analytic", "stock_account"],
    "data": [
        "views/stock_quant_view.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
