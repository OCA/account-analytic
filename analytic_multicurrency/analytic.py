# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joël Grand-Guillaume
#    Author: Grand-Guillaume Joel
#    Copyright 2011-2013 Camptocamp SA
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
    _inherit = 'account.analytic.account'

    def _debit_credit_bal_qtty(self, cr, uid, ids, fields, arg, context=None):
        """Replace the original amount column by aa_amount_currency"""
        if context is None:
            context = {}
        child_ids = self.search(cr, uid,
                                [('parent_id', 'child_of', ids)],
                                context=context)
        sums = {}
        if not child_ids:
            return sums
        for child_id, field in product(child_ids, name):
            sums.setdefault(child_id, {})[name] = 0.0

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date'):
            where_date += " AND l.date >= %s"
            where_clause_args += [context['from_date']]
        if context.get('to_date'):
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
            sums[ac_id] = {'debit': debit,
                           'credit': credit,
                           'balance': balance,
                           'quantity': quantity}
        return self._compute_level_tree(cr, uid, ids, child_ids, sums,
                                        ['debit', 'credit',
                                         'balance', 'quantity'],
                                        context)

    _columns = {
        'balance': fields.function(_debit_credit_bal_qtty,
                                   type='float',
                                   string='Balance',
                                   multi='debit_credit_bal_qtty',
                                   digits_compute=dp.get_precision('Account')),
        'debit': fields.function(_debit_credit_bal_qtty,
                                 type='float',
                                 string='Debit',
                                 multi='debit_credit_bal_qtty',
                                 digits_compute=dp.get_precision('Account')),
        'credit': fields.function(_debit_credit_bal_qtty,
                                  type='float',
                                  string='Credit',
                                  multi='debit_credit_bal_qtty',
                                  digits_compute=dp.get_precision('Account')),
        'quantity': fields.function(_debit_credit_bal_qtty,
                                    type='float',
                                    string='Quantity',
                                    multi='debit_credit_bal_qtty'),
    }

    # We remove the currency constraint cause we want to let the user
    # choose another currency than the company one. Don't be able to
    # override properly this constraints :(
    def check_currency(self, cr, uid, ids, context=None):
        return True

    def check_recursion(self, cr, uid, ids, parent=None):
        return super(account_analytic_account, self)._check_recursion(
            cr, uid, ids, parent=parent)

    _constraints = [
        (check_recursion,
         'Error. You can not create recursive analytic accounts.',
         ['parent_id']),
        (check_currency,
         'Error. The currency has to be the same as the currency of '
         'the selected company.',
         ['currency_id', 'company_id']),
    ]
