# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#                  2013 Markus SChneider <markus.schneider@initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Account Analytic Line List",
    "version": "1.1",
    "author": "initOS GmbH & Co. KG,Odoo Community Association (OCA)",
    "website": "www.initos.com",
    "category": "Generic Modules/Projects & Services",
    "description": """Adds a wizard on financial reporting to search
        the analytic lines for a given analytic account including all
        their child accounts. Ported module acy_account_analytic_lines
        from Acysos S.L. (Sponsored by Talleres Mutilva)""",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "analytic"
    ],
    "data": ["wizard/account_analytic_line.xml"],
    "demo": [],
    "active": False,
    "installable": False,
}
