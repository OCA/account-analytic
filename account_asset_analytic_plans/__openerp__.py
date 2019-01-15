# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Analytic plans in asset management",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "summary": "Use analytic plans in assets",
    "depends": [
        'account_asset',
        'account_analytic_plans',
    ],
    "data": [
        "views/account_asset_asset.xml",
        "views/account_asset_category.xml",
    ],
    "auto_install": True,
}
