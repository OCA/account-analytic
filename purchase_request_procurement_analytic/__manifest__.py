# -*- coding: utf-8 -*-
# Copyright 2019 Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Request Procurement Analytic',
    'summary': 'This module sets analytic account in purchase request line '
               'from procurement analytic account',
    'version': '10.0.1.0.0',
    'category': 'Analytic',
    'license': 'AGPL-3',
    'author': "Akretion, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.github.com/oca/manufacture',
    'depends': [
        'purchase_request_procurement',
        'procurement_analytic',
    ],
    'installable': True,
}
