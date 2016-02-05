# -*- coding: utf-8 -*-
# © 2013 Julius Network Solutions
# © 2015 Clear Corp
# © 2016 Andhitia Rama <andhitia.r@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Analytic",
    "summary": "Adds an analytic account in stock move",
    "version": "8.0.1.0.0",
    "author": "Julius Network Solutions,"
    "ClearCorp, Andhitia Rama, "
    "Odoo Community Association (OCA)",
    "website": "http://www.julius.fr/",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "depends": [
        "stock_account",
        "analytic",
    ],
    "data": [
        "views/stock_move_views.xml",
        "views/stock_inventory_views.xml",
    ],
    'installable': True,
    'active': False,
}
