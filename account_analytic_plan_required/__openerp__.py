# -*- encoding: utf-8 -*-
##############################################################################
#
#    Account analytic plan required module for OpenERP
#    Copyright (C) 2014 Acsone (http://acsone.eu).
#    @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
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
    'name': 'Account Analytic Plan Required',
    'version': '8.0.0.1.0',
    'category': 'Analytic Accounting',
    'license': 'AGPL-3',
    'description': """
Account Analytic Plan Required
==============================

This module extends account_analytic_required and adds 2 policies to
control the use of analytic distributions. The policies behave as follow
* never: no analytic account nor analytic distribution allowed
* always: analytic account required
* always_plan: analytic_distribution required
* always_plan_or_account: analytic distribution or analytic account required
* optional: do what you like,

In any case analytic account and analytic distribution are mutually exclusive.
""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': 'http://www.acsone.eu/',
    'depends': ['account_analytic_required', 'account_analytic_plans'],
    'data': [],
    'installable': True,
}
