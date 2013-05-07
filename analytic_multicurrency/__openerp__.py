# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Grand-Guillaume Joel
#    Copyright 2010-2013 Camptocamp SA
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
 "name": "Multi-Currency in Analytic Accounting",
 "version": "1.0",
 "author": "Camptocamp",
 "license": 'AGPL-3',
 "category": "Generic Modules/Accounting",
 "description":
"""
Multi-Currency in Analytic Accounting
=====================================

This module improves OpenERP multi-currency handling in analytic
accounting, overall for multi-company.

This module is based on the work made in all c2c_multicost* available on
the v5.0 stable version and allows you to share analytic account between
company (even if currency differs in each one).

Features:

* Adapt the owner of analytic line (= to company that own the general
  account associated with an analytic line)

* Add multi-currency on analytic lines (similar to financial accounting)

* Correct all "costs" indicators into analytic account to base them on
  the right currency (owner's company)

* By default, nothing changes for single company implementation.

As a result, we can now really share the same analytic account between
companies that do not have the same currency. This setup becomes True,
Enjoy !

* Company A: EUR - Company B: CHF

* Analytic Account A: USD, owned by Company A

  - Analytic Account B: CHF, owned by Company A

  - Analytic Account C: EUR, owned by Company B


The difference with the regular 'Amount Currency':

* Regular 'Amount Currency' displays the amount currency of the related
  move line (only when linked with a move line, of course)
* Analytic Amount Currency displays the amount of the analytic move line
  converted to the right currency

""",
 "website": "http://camptocamp.com",
 "depends": ["account",
             "analytic",
             "account_analytic_analysis",
             ],
 "data": ["analytic_view.xml",
          ],
 "installable": True
}
