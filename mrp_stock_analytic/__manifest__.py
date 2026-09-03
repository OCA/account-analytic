# Copyright 2023 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Stock Analytic",
    "summary": "Adds analytic distribution in manufacturing order",
    "version": "18.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Manufacturing/Manufacturing",
    "license": "AGPL-3",
    "depends": ["mrp_account", "stock_analytic"],
    "data": [
        "wizard/mrp_wip_accounting_views.xml",
        "views/mrp_production_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
