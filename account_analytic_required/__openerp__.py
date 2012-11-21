# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account analytic required module for OpenERP
#    Copyright (C) 2011 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Account analytic required',
    'version': '0.1',
    'category': 'Generic Modules/Accounting',
    'license': 'AGPL-3',
    'description': """This module adds an option "analytic policy" on account types. You have the choice between 3 policies : always, never and optional.

For example, if you want to have an analytic account on all your expenses, set the policy to "always" for the account type "expense" ; then, if you try to save an account move line with an account of type "expense" without analytic account, you will get an error message.

Module developped by Alexis de Lattre <alexis.delattre@akretion.com> during the Akretion-Camptocamp code sprint of June 2011.
""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': ['account_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}

