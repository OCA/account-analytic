# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro Manuel Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'HR expenses analytic distribution',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """
The base module to manage analytic distribution on HR expenses
==============================================================

Using this module, you will be able to link analytic distributions to expenses.
    """,
    'author': "Serv. Tecnolog. Avanzados - Pedro M. Baeza,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'hr_expense',
        'account_analytic_plans',
    ],
    'data': [
        'view/hr_expense_analytic_plans_view.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
