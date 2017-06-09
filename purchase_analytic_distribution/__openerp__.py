# -*- coding: utf-8 -*-
#  Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#  Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase Analytic Plans",
    "version": "9.0.1.0.0",
    "category": "Purchase Management",
    "author": "OpenERP SA, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo.com/page/purchase",
    "license": "AGPL-3",
    "depends": [
        "purchase",
        "account_analytic_distribution",
    ],
    "data": [
        "views/purchase_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
