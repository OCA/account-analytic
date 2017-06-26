# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Invoice to the other partner',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'summary': 'Invoice analytic lines for the other partner',
    'category': 'Human Resources',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'analytic_partner_hr_timesheet',
        'analytic_partner',
        'sale_timesheet',
    ],
    'data': [
    ],
    'installable': True,
    "auto_install": True,
}
