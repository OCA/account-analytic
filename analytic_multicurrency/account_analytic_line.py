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

from openerp.osv import orm, fields
import openerp.addons.decimal_precision as dp


class account_analytic_line(orm.Model):
    _inherit = 'account.analytic.line'

    def _amount_currency(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids, context=context):
            cmp_cur_id = line.company_id.currency_id.id
            aa_cur_id = line.account_id.currency_id.id
            # Always provide the amount in currency
            if cmp_cur_id == aa_cur_id:
                result[line.id] = line.amount
            else:
                ctx = context.copy()
                if not (line.date and line.amount):
                    continue
                ctx['date'] = line.date
                result[line.id] = cur_obj.compute(cr, uid,
                                                  cmp_cur_id,
                                                  aa_cur_id,
                                                  line.amount,
                                                  context=ctx)
        return result

    def _get_account_currency(self, cr, uid, ids, field_name, arg,
                              context=None):
        result = {}
        for line in self.browse(cr, uid, ids, context=context):
            # Always provide second currency
            result[line.id] = (line.account_id.currency_id.id,
                               line.account_id.currency_id.name)
        return result

    def _get_account_line(self, cr, uid, ids, context=None):
        aa_line_obj = self.pool.get('account.analytic.line')
        return aa_line_obj.search(cr, uid,
                                  [('account_id', 'in', ids)],
                                  context=context)

    # Add the account currency and amount in this currency on each
    # analytic line.
    # The company_id of analytic line is always related to the company
    # of the general account linked on the line
    _columns = {
        'aa_currency_id': fields.function(
            _get_account_currency,
            type='many2one',
            relation='res.currency',
            string='Analytic Account currency',
            store={
                'account.analytic.account': (_get_account_line,
                                             ['currency_id', 'company_id'],
                                             50),
                'account.analytic.line': (lambda self, cr, uid, ids, c=None:
                                          ids,
                                          ['amount',
                                           'unit_amount',
                                           'product_uom_id'],
                                          10),
            },
            help="The related analytic account currency."),
        'aa_amount_currency': fields.function(
            _amount_currency,
            string='Analytic Amount currency',
            digits_compute=dp.get_precision('Account'),
            store={
                'account.analytic.account': (_get_account_line,
                                             ['currency_id', 'company_id'],
                                             50),
                'account.analytic.line': (lambda self, cr, uid, ids, c=None:
                                          ids,
                                          ['amount',
                                           'unit_amount',
                                           'product_uom_id'],
                                          10),
            },
            help="The amount expressed in the related analytic account "
                 "currency."),
        'company_id': fields.related(
            'general_account_id',
            'company_id',
            type='many2one',
            relation='res.company',
            string='Company',
            store=True,
            readonly=True),
    }

    def on_change_unit_amount(self, cr, uid, ids, prod_id, quantity,
                              company_id, unit=False, journal_id=False,
                              context=None):
        if context is None:
            context = {}
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr, uid, company_id, context=context)
        ctx = context.copy()
        ctx['currency_id'] = company.currency_id.id
        return super(account_analytic_line, self).on_change_unit_amount(
            cr, uid, ids, prod_id, quantity, company_id,
            unit=unit, journal_id=journal_id, context=ctx)
