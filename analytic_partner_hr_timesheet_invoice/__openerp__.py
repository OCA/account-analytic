# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Invoice to the partner in analytic lines',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'summary': 'Invoice analytic lines for the specific partner in them',
    'category': 'Human Resources',
    'author': 'Antiun Ingeniería S.L., '
              'Serv. Tecnol. Avanzados - Pedro M. Baeza, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.antiun.com',
    'depends': [
        'analytic_partner',
        'hr_timesheet_invoice',
    ],
    'data': [
    ],
    "installable": True,
    "auto_install": True,
}
