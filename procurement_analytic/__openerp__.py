# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Procurement Analytic',
    'summary': 'This module adds analytic account to procurements',
    'version': '8.0.1.0.0',
    'category': 'Analytic',
    'license': 'AGPL-3',
    'author': "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.tecnativa.com',
    'depends': [
        'procurement',
        'analytic',
    ],
    'data': [
        'views/procurement_analytic.xml',
    ],
    'installable': True,
}
