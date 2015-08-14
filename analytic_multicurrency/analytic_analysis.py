# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-Guillaume
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

from itertools import product
from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class account_analytic_account(orm.Model):
    _inherit = "account.analytic.account"

    def _ca_invoiced_calc(self, cr, uid, ids, name, arg, context=None):
        """Replace the original amount column by aa_amount_currency"""
        child_ids = self.search(cr, uid,
                                [('parent_id', 'child_of', ids)],
                                context=context)
        sums = {}
        for child_id, field in product(child_ids, name):
            sums.setdefault(child_id, {})[name] = 0.0

        sql = ("SELECT account_analytic_line.account_id, "
               "       COALESCE(SUM(aa_amount_currency), 0.0) "
               "FROM account_analytic_line "
               "JOIN account_analytic_journal "
               "ON account_analytic_line.journal_id = "
               "account_analytic_journal.id "
               "WHERE account_analytic_line.account_id IN %s "
               "AND account_analytic_journal.type = 'sale' "
               "GROUP BY account_analytic_line.account_id")
        cr.execute(sql, (tuple(child_ids),))

        precision_obj = self.pool.get('decimal.precision')
        precision = precision_obj.precision_get(cr, uid, 'Account')
        for account_id, row_sum in cr.fetchall():
            sums[account_id][name] = round(row_sum, precision)
        data = self._compute_level_tree(cr, uid, ids, child_ids,
                                        sums, [name], context=context)
        return dict((account_id, row[name]) for account_id, row
                    in data.iteritems())

    def _total_cost_calc(self, cr, uid, ids, name, arg, context=None):
        """Replace the original amount column by aa_amount_currency"""
        child_ids = self.search(cr, uid,
                                [('parent_id', 'child_of', ids)],
                                context=context)
        sums = {}
        for child_id, field in product(child_ids, name):
            sums.setdefault(child_id, {})[name] = 0.0

        sql = ("SELECT account_analytic_line.account_id, "
               "       COALESCE(SUM(aa_amount_currency), 0.0) "
               "FROM account_analytic_line "
               "JOIN account_analytic_journal "
               "ON account_analytic_line.journal_id "
               " = account_analytic_journal.id "
               "WHERE account_analytic_line.account_id IN %s "
               "AND amount < 0 "
               "GROUP BY account_analytic_line.account_id")
        cr.execute(sql, (tuple(child_ids),))

        precision_obj = self.pool.get('decimal.precision')
        precision = precision_obj.precision_get(cr, uid, 'Account')
        for account_id, row_sum in cr.fetchall():
            sums[account_id][name] = round(row_sum, precision)
        data = self._compute_level_tree(cr, uid, ids, child_ids,
                                        sums, [name], context)
        return dict((account_id, row[name]) for account_id, row
                    in data.iteritems())

    _columns = {
        'ca_invoiced': fields.function(
            _ca_invoiced_calc,
            type='float',
            string='Invoiced Amount',
            help="Total customer invoiced amount for "
                 "this account.",
            digits_compute=dp.get_precision('Account')),
        'total_cost': fields.function(
            _total_cost_calc,
            type='float',
            string='Total Costs',
            help="Total of costs for this account. "
                 "It includes real costs (from "
                 "invoices) and indirect costs, "
                 "like time spent on timesheets.",
            digits_compute=dp.get_precision('Account')),
    }
