# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Link analytic items and partner',
    'summary': 'Search and group analytic entries by partner',
    'version': '10.0.1.0.0',
    'category': 'Analytic Accounting',
    'website': 'https://www.tecnativa.com',
    'author': 'Tecnativa,'
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'account',
    ],
    'data': [
        'views/account_analytic_line_views.xml',
        'views/res_partner_views.xml',
    ],
}
