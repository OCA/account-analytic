# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Inventory Analytic",
    "summary": """
        Stock Inventory Analytic """,
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Warehouse Management",
    "version": "19.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["analytic", "stock_analytic", "stock_account"],
    "data": [
        "views/res_config_settings_views.xml",
        "wizards/stock_inventory_adjustment_name.xml",
    ],
    "installable": True,
}
