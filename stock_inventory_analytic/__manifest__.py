# Copyright 2019 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Stock Inventory Analytic",
    "summary": """
        Stock Inventory Analytic """,
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Warehouse Management",
    "version": "14.0.1.0.3",
    "license": "AGPL-3",
    "depends": ["analytic", "stock_analytic", "stock_account"],
    "data": [
        "views/stock_inventory_line_view.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
}
