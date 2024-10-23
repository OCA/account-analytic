# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Analytic",
    "summary": "Adds analytic distribution in stock move",
    "version": "17.0.1.2.0",
    "author": "Julius Network Solutions, "
    "ClearCorp, OpenSynergy Indonesia, "
    "Hibou Corp., "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-analytic",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": ["stock_account", "analytic"],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_scrap_views.xml",
        "views/stock_move_line_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
}
