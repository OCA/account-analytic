# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Distribution asset analytic",
    "summary": "Adds analytic distribution per asset",
    "version": "8.0.1.0.0",
    "category": "Analytic Accounting",
    "website": "http://praxya.com/",
    "author": "Tecnativa, "
              "Praxya, "
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
