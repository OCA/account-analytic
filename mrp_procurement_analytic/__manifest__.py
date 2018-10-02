# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mrp Procurement Analytic',
    'summary': """
        Makes the link between procurement analytic account and moves created
        trhough MRP""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://acsone.eu',
    'depends': [
        'mrp',
        'mrp_analytic',
        'procurement_analytic',
        'stock_analytic',
    ],
}
