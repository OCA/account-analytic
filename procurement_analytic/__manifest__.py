# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement Analytic',
    'summary': 'This module adds analytic account to procurements',
    'version': '10.0.1.1.0',
    'category': 'Analytic',
    'license': 'AGPL-3',
    'author': "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://www.tecnativa.com',
    'depends': [
        'procurement',
        'analytic',
    ],
    'data': [
        'views/account_analytic_account_view.xml',
        'views/procurement_analytic.xml',
    ],
    'installable': True,
}
