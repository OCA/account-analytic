# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Analytic Parent',
    'summary': """
        This module reintroduces the hierarchy to the analytic accounts.""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Matmoz d.o.o., '
              'Luxim d.o.o., '
              'Deneroteam, '
              'Eficent, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/account-analytic.git',
    'depends': [
        'account_accountant',
        'analytic',
    ],
    'data': [
        'views/account_analytic_account_view.xml',
        'wizard/account_analytic_chart_view.xml',
    ],
    'demo': [
        'data/analytic_account_demo.xml',
    ],
}
