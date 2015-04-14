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


class project_activity_al(osv.osv):

    """Class that inhertis osv.osv and add 2nd analytic axe to account analytic
    lines.
    The _name is kept for previous version compatibility (project.activity_al).
    """
    # Keep that name for back -patibility
    _name = "project.activity_al"
    _description = "Second Analytical Axes"

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        acc_ids = []
        if context is None:
            context = {}
        if context.get('from_date', False):
            args.append(['date', '>=', context['from_date']])
        if context.get('to_date', False):
            args.append(['date', '<=', context['to_date']])

        if context.get('account_id', False):
            aa_obj = self.pool.get('account.analytic.account')
            account_id = aa_obj.browse(
                cr, uid, context.get('account_id', False))
            # take the account wich have activity_ids
            acc_who_matters = self._get_first_AA_wich_have_activity(
                cr,
                uid,
                account_id
            )
            if acc_who_matters:
                for i in acc_who_matters.activity_ids:
                    acc_ids.append(i.id)
                args.append(('id', 'in', acc_ids))

        return super(project_activity_al, self).search(
            cr, uid, args, offset, limit, order, context=context, count=count)

    # @param self The object pointer.
    # @param cr a psycopg cursor.
    # @param uid res.user.id that is currently loged
    # @param account a browse record of an account
    # @return a browse reccod list of the first parent that have an activites
    def _get_first_AA_wich_have_activity(self, cr, uid, account):
        """Return browse record list of activities
           of the account which have an activity set
           (goes bottom up, child, then parent)
        """
        if account.activity_ids:
            return account
        else:
            if account.parent_id:
                return self._get_first_AA_wich_have_activity(cr, uid,
                                                             account.parent_id)
            else:
                return False

    # @param self The object pointer.
    # @param cr a psycopg cursor.
    # @param uid res.user.id that is currently loged
    # @param name osv._obj name of the serached object
    # @param args an arbitrary list that contains search criterium
    # @param operator search operator
    # @param context an arbitrary context
    # @param limit int of the search limit
    # @return the result of name get
    def name_search(self, cr, uid, name, args=None,
                    operator='ilike', context=None, limit=80):
        """ Ovveride of osv.osv name serach function that do the search
            on the name of the activites """
        if not args:
            args = []
        if not context:
            context = {}

        account = self.search(
            cr,
            uid,
            [
                ('code', '=', name),
                # ('id','in',acc_ids)
            ] + args,
            limit=limit,
            context=context
        )
        if not account:
            account = self.search(
                cr,
                uid,
                [
                    ('name', 'ilike', '%%%s%%' % name),
                    # ('id','in',acc_ids)
                ] + args,
                limit=limit,
                context=context
            )
        if not account:
            account = self.search(
                cr,
                uid,
                [
                    # ('id','in',acc_ids)
                ] + args,
                limit=limit,
                context=context
            )
        # For searching in parent also
        if not account:
            account = self.search(
                cr,
                uid,
                [
                    ('name', 'ilike', '%%%s%%' % name)
                ] + args,
                limit=limit,
                context=context
            )
            newacc = account
            while newacc:
                newacc = self.search(
                    cr,
                    uid,
                    [
                        ('parent_id', 'in', newacc)
                    ] + args,
                    limit=limit,
                    context=context
                )
                account += newacc

        return self.name_get(cr, uid, account, context=context)

    def _compute_level_tree(self, cr, uid, ids, child_ids, res, field_names,
                            context=None):
        def recursive_computation(account_id, res):
            currency_obj = self.pool.get('res.currency')
            account = self.browse(cr, uid, account_id)
            for son in account.child_ids:
                res = recursive_computation(son.id, res)
                for field in field_names:
                    if (
                        account.currency_id.id == son.currency_id.id
                        or field == 'quantity'
                    ):
                        res[account.id][field] += res[son.id][field]
                    else:
                        res[account.id][field] += currency_obj.compute(
                            cr, uid, son.currency_id.id,
                            account.currency_id.id, res[son.id][field],
                            context=context)
            return res
        for account in self.browse(cr, uid, ids, context=context):
            if account.id not in child_ids:
                continue
            res = recursive_computation(account.id, res)
        return res

    def _debit_credit_bal_qtty(self, cr, uid, ids, name, arg, context=None):
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
                         CASE WHEN l.amount > 0
                         THEN l.amount
                         ELSE 0.0
                         END
                          ) as debit,
                     sum(
                         CASE WHEN l.amount < 0
                         THEN -l.amount
                         ELSE 0.0
                         END
                          ) as credit,
                     COALESCE(SUM(l.amount),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity
              FROM project_activity_al a
                  LEFT JOIN account_analytic_line l ON (a.id = l.activity)
              WHERE a.id IN %s
              """ + where_date + """
              GROUP BY a.id""", where_clause_args)
        for ac_id, debit, credit, balance, quantity in cr.fetchall():
            res[ac_id] = {'debit': debit, 'credit': credit,
                          'balance': balance, 'quantity': quantity}
        return self._compute_level_tree(cr, uid, ids, child_ids, res, [
            'debit', 'credit', 'balance', 'quantity'
        ], context)

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('res.company').search(
            cr, uid, [('parent_id', '=', False)]
        )[0]

    def _get_default_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.currency_id.id

    _columns = {
        # activity code
        'code': fields.char('Code', required=True, size=64),
        # name of the code
        'name': fields.char('Activity', required=True, size=64,
                            translate=True),
        # parent activity
        'parent_id': fields.many2one('project.activity_al', 'Parent activity'),
        # link to account.analytic account
        'project_ids': fields.many2many(
            'account.analytic.account',
            'proj_activity_analytic_rel',
            'activity_id', 'analytic_id',
            'Concerned Analytic Account'
        ),
        # link to the children activites
        'child_ids': fields.one2many(
            'project.activity_al',
            'parent_id',
            'Childs Activities'
        ),
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
            string='Quantity',
            multi='debit_credit_bal_qtty'),
        'currency_id': fields.many2one(
            'res.currency',
            'Activity currency',
            required=True),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=False),
    }

    _defaults = {
        'company_id': _default_company,
        'currency_id': _get_default_currency,
    }


class analytic_account(osv.osv):
    _inherit = "account.analytic.account"

    _columns = {
        # Link activity and project
        'activity_ids': fields.many2many(
            'project.activity_al',
            'proj_activity_analytic_rel',
            'analytic_id',
            'activity_id',
            'Related activities'
        ),

    }


class account_analytic_line(osv.osv):
    _name = "account.analytic.line"
    _inherit = "account.analytic.line"

    _columns = {
        'activity': fields.many2one('project.activity_al', 'Activity'),
    }
