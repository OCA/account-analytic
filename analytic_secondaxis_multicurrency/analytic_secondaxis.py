# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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

from osv import fields
from osv import osv
import decimal_precision as dp

##########################################################################
#  employee activity
##########################################################################


class project_activity_al(osv.osv):

    """Class that inhertis osv.osv and add 2nd analytic axe to account analytic
    lines. The _name is kept for previous version compatibility
    (project.activity_al)."""
    # Keep that name for back -patibility
    _inherit = "project.activity_al"
    _description = "Second Analytical Axes"

    def _debit_credit_bal_qtty(self, cr, uid, ids, name, arg, context=None):
        """Replace the original amount column by aa_amount_currency"""
        res = {}
        if context is None:
            context = {}
        child_ids = tuple(
            self.search(cr, uid, [('parent_id', 'child_of', ids)]))
        for i in child_ids:
            res[i] = {}
            for n in name:
                res[i][n] = 0.0

        if not child_ids:
            return res

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date', False):
            where_date += " AND l.date >= %s"
            where_clause_args += [context['from_date']]
        if context.get('to_date', False):
            where_date += " AND l.date <= %s"
            where_clause_args += [context['to_date']]
        cr.execute("""
              SELECT a.id,
                     sum(
                         CASE WHEN l.aa_amount_currency > 0
                         THEN l.aa_amount_currency
                         ELSE 0.0
                         END
                          ) as debit,
                     sum(
                         CASE WHEN l.aa_amount_currency < 0
                         THEN -l.aa_amount_currency
                         ELSE 0.0
                         END
                          ) as credit,
                     COALESCE(SUM(l.aa_amount_currency),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity
              FROM account_analytic_account a
                  LEFT JOIN account_analytic_line l ON (a.id = l.account_id)
              WHERE a.id IN %s
              """ + where_date + """
              GROUP BY a.id""", where_clause_args)
        for ac_id, debit, credit, balance, quantity in cr.fetchall():
            res[ac_id] = {'debit': debit, 'credit': credit,
                          'balance': balance, 'quantity': quantity}
        return self._compute_level_tree(cr, uid, ids, child_ids, res, [
            'debit', 'credit', 'balance', 'quantity'
        ], context)

    _columns = {
        'balance': fields.function(
            _debit_credit_bal_qtty,
            method=True,
            type='float',
            string='Balance',
            multi='debit_credit_bal_qtty',
            digits_compute=dp.get_precision('Account')),
        'debit': fields.function(
            _debit_credit_bal_qtty,
            method=True,
            type='float',
            string='Debit',
            multi='debit_credit_bal_qtty',
            digits_compute=dp.get_precision('Account')),
        'credit': fields.function(
            _debit_credit_bal_qtty,
            method=True,
            type='float',
            string='Credit',
            multi='debit_credit_bal_qtty',
            digits_compute=dp.get_precision('Account')),
        'quantity': fields.function(
            _debit_credit_bal_qtty,
            method=True,
            type='float',
            string='Quantity', multi='debit_credit_bal_qtty'),
    }

project_activity_al()
