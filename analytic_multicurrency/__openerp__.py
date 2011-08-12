# -*- coding: utf-8 -*-
##############################################################################
#
# @author Grand-Guillaume Joel
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

{
     "name" : "Multi-Currency in Analytic",
     "version" : "1.0",
     "author" : "Camptocamp",
     "category" : "Generic Modules/Accounting",
     "description":
"""
This improve OpenERP multi-currency handling in analytic accountiong, overall for multi-company.

This module is based on the work made in all c2c_multicost* available on the v5.0 stable version and
allow you to shar analytic account between company (even if currency differs in each one).

What has been done here:

  * Adapt the owner of analytic line (= to company that own the general account associated with en analytic line)
  * Add multi-currency on analytic lines (similar to financial accounting)
  * Correct all "costs" indicators into analytic account to base them on the right currency (owner's company)
  * By default, nothing change for single company implementation.

As a result, we can now really share the same analytic account between companies that doesn't have the same 
currency. This setup becomes True, Enjoy !

- Company A : EUR
- Company B : CHF

- Analytic Account A : USD, owned by Company A
    - Analytic Account B : CHF, owned by Company A
    - Analytic Account C : EUR, owned by Company B


""",
     "website": "http://camptocamp.com",
     "depends" : ["account",
                 "analytic",
                 "account_analytic_analysis",
                ],
     "init_xml" : [],
     "demo_xml" : [],
     "update_xml" : [
          "analytic_view.xml",
     ],
     "active": False,
     "installable": True
}
