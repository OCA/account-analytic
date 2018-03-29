# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Analytic account code sequence',
    'summary': 'Analytic account code sequence',
    'version': '10.0.1.0.0',
    'author':   'Eficent, '
                'SerpentCS ,'
                'Project Expert Team ,'
                'Odoo Community Association (OCA)',
    'website': 'https://www.github.com/OCA/account-analytic',
    'category': 'Analytic',
    'depends': ['analytic', 'account_analytic_parent'],
    'data': [
        'views/analytic_account_sequence_view.xml',
        'data/analytic_account_sequence_data.xml',
        'views/account_analytic_account_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
