# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Partner in analytics',
    'version': '8.0.1.0.0',
    'summary': 'Classify analytic entries by partner',
    'category': 'Analytic Accounting',
    'author': 'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Antiun Ingeniería S.L., '
              'Odoo Community Association (OCA)',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'analytic',
        'account',
    ],
    'data': [
        'views/account_analytic_line_views.xml',
        'views/res_partner_views.xml',
    ],
    "installable": True,
}
