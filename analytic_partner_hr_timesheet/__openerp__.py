# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Partner in HR timesheets',
    'version': '8.0.1.0.0',
    'summary': 'Classify HR activities by partner',
    'category': 'Human Resources',
    'author': 'Antiun Ingeniería S.L., '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'depends': [
        'analytic_partner',
        'hr_timesheet',
    ],
    'data': [
        'views/hr_analytic_timesheet_views.xml',
        'views/res_partner_views.xml',
    ],
    "installable": True,
    "auto_install": True,
}
