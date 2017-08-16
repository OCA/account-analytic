# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Partner in HR timesheets',
    'version': '10.0.1.0.0',
    'summary': 'Classify HR activities by partner',
    'category': 'Human Resources',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'analytic_partner',
        'hr_timesheet',
    ],
    'data': [
        'views/hr_analytic_timesheet_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    "auto_install": True,
}
