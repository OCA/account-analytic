# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Link analytic items and partner',
    'summary': 'Search and group analytic entries by partner',
    'version': '10.0.1.0.0',
    'category': 'Analytic Accounting',
    'website': 'http://www.serviciosbaeza.com',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Antiun Ingeniería S.L., '
              'Odoo Community Association (OCA)',
    "License": "AGPL-3",
    "installable": True,
    'depends': [
        'analytic',
        'account',
    ],
    'data': [
        'views/account_analytic_line_views.xml',
        'views/res_partner_views.xml',
    ],
}
