# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Procurement Analytic',
    'summary': 'This module sets analytic account in purchase order line from '
               'procurement analytic account',
    'version': '10.0.1.0.0',
    'category': 'Analytic',
    'license': 'AGPL-3',
    'author': "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.tecnativa.com',
    'depends': [
        'purchase',
        'procurement_analytic',
    ],
    'installable': True,
}
