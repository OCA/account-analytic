# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Purchase Contract Analysis',
    'version': '8.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Create a purchase contract',
    'author': 'KMEE, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.kmee.com.br',
    'depends': [
        'account_budget',
        'account_analytic_analysis',
    ],
    'data': [
        'views/account_budget_view.xml',
    ],
    'installable': True,
}
