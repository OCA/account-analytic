# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Luis M. Ontalba - <luis.martinez@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account asset analytic",
    "summary": "Adds analytic account per asset",
    "version": "10.0.1.0.0",
    "category": "Analytic Accounting",
    "website": "https://www.tecnativa.com",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "account_asset",
    ],
    "data": [
        "views/account_asset_asset_view.xml",
    ],
}
