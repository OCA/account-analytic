# -*- coding: utf-8 -*-
# Copyright 2019 Abraham Anes - <abraham@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Asset Analytic Distribution',
    'summary': 'Adds analytic distribution per asset',
    'version': '10.0.1.0.0',
    'category': 'Analytic Accounting',
    'license': 'AGPL-3',
    'author': 'Studio73, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/account-analytic',
    'depends': [
        'account_asset',
        'account_analytic_distribution',
    ],
    'data': [
        'views/account_asset_asset_view.xml',
    ],
}
