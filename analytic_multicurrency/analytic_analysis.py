# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camtocamp SA
# @author Joël Grand-Guillaume
# $Id: $
#
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

import operator
from osv import osv, fields
from osv.orm import intersect
import tools.sql 
from tools.translate import _
import decimal_precision as dp

class account_analytic_account(osv.osv):
    _inherit = "account.analytic.account"

    def _ca_invoiced_calc(self, cr, uid, ids, name, arg, context=None):
        """Replace the original amount column by aa_amount_currency"""
        res = {}
        res_final = {}
        child_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context))
        for i in child_ids:
            res[i] =  {}
            for n in [name]:
                res[i][n] = 0.0
        if not child_ids:
            return res

        if child_ids:
            cr.execute("SELECT account_analytic_line.account_id, COALESCE(SUM(aa_amount_currency), 0.0) \
                    FROM account_analytic_line \
                    JOIN account_analytic_journal \
                        ON account_analytic_line.journal_id = account_analytic_journal.id  \
                    WHERE account_analytic_line.account_id IN %s \
                        AND account_analytic_journal.type = 'sale' \
                    GROUP BY account_analytic_line.account_id", (child_ids,))
            for account_id, sum in cr.fetchall():
                res[account_id][name] = round(sum,2)
        data = self._compute_level_tree(cr, uid, ids, child_ids, res, [name], context=context)
        for i in data:
            res_final[i] = data[i][name]
        return res_final

    def _total_cost_calc(self, cr, uid, ids, name, arg, context=None):
        """Replace the original amount column by aa_amount_currency"""
        res = {}
        res_final = {}
        child_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context))

        for i in child_ids:
            res[i] =  {}
            for n in [name]:
                res[i][n] = 0.0
        if not child_ids:
            return res

        if child_ids:
            cr.execute("""SELECT account_analytic_line.account_id, COALESCE(SUM(aa_amount_currency), 0.0) \
                    FROM account_analytic_line \
                    JOIN account_analytic_journal \
                        ON account_analytic_line.journal_id = account_analytic_journal.id \
                    WHERE account_analytic_line.account_id IN %s \
                        AND amount<0 \
                    GROUP BY account_analytic_line.account_id""",(child_ids,))
            for account_id, sum in cr.fetchall():
                res[account_id][name] = round(sum,2)
        data = self._compute_level_tree(cr, uid, ids, child_ids, res, [name], context)
        for i in data:
            res_final[i] = data[i][name]
        return res_final
        
    _columns ={
    'ca_invoiced': fields.function(_ca_invoiced_calc, method=True, type='float', string='Invoiced Amount',
        help="Total customer invoiced amount for this account.",
        digits_compute=dp.get_precision('Account')),
    'total_cost': fields.function(_total_cost_calc, method=True, type='float', string='Total Costs',
        help="Total of costs for this account. It includes real costs (from invoices) and indirect costs, like time spent on timesheets.",
        digits_compute=dp.get_precision('Account')),
     }
account_analytic_account()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

