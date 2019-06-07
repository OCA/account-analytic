##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV <http://therp.nl>
#    All Rights Reserved
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
    'name': 'Project and analytic account integration',
    'description': """
Project and analytic account integration.

Gives the option to create projects directly from the analytic accounts they
should be linked to.

Without this module, if you first create an analytic account and later on you
decide to have a project as well for this account, the situation is very
difficult to rectify.
""",
    'version': '1.0',
    'author': 'Therp BV',
    'category': 'Generic Modules/Accounting',
    'website': 'http://therp.nl',
    'email': 'info@therp.nl',
    'depends': [
        'account',
        'project',
    ],
    'update_xml': [
        'view/account_analytic_account.xml',
    ],
    'license': 'AGPL-3',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
