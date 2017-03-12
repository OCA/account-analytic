# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Analytic No Lines',
    'summary': """
        This module hides analytics lines from accounting menus and disable
         their generation from an invoice or a move line.""",
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu/',
    'depends': [
        'account',
        'analytic',
    ],
    'data': [
        'views/account_analytic_account.xml',
        'data/data_account_analytic_group.xml',
        'views/account_analytic.xml',
    ],
}
