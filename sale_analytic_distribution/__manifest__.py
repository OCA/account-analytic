# -*- coding: utf-8 -*-
#  Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#  Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Sales Analytic Distribution",
    "version": "10.0.1.0.0",
    "category": "Sales Management",
    "author": "Odoo SA,"
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://www.tecnativa.com",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "account_analytic_distribution",
    ],
    "data": [
        "views/sale_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
