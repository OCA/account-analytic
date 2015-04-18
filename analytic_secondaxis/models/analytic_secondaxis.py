# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# Copyright (c) 2015 Taktik SA (http://www.taktik.be)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
# Author : Adil Houmadi (Taktik)
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

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class ProjectActivityAl(models.Model):
    _name = 'project.activity_al'
    _description = 'Second Analytical Axes'
    _rec_name = 'display_name'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        analytic_account_ids = []
        if self._context.get('from_date', False):
            args.append(['date', '>=', self._context['from_date']])
        if self._context.get('to_date', False):
            args.append(['date', '<=', self._context['to_date']])
        if self._context.get('account_id', False):
            analytic_account_obj = self.env['account.analytic.account']
            analytic_account = analytic_account_obj.browse(
                self._context.get('account_id'))
            # take the account which have activity_ids
            aa_activities = False
            if analytic_account.activity_ids:
                aa_activities = analytic_account
            else:
                while analytic_account.parent_id:
                    analytic_account = analytic_account.parent_id
                    if analytic_account.activity_ids:
                        aa_activities = analytic_account
                        break
            if aa_activities:
                for temp_account in aa_activities:
                    analytic_account_ids.append(temp_account.id)
                args.append(('id', 'in', analytic_account_ids))
        return super(ProjectActivityAl, self).search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count
        )

    def recursive_computation(self, account_id, field_names):
        currency_obj = self.env['res.currency']
        account = self.browse(account_id)
        for son in account.child_ids:
            self.recursive_computation(son.id, field_names)
            for field in field_names:
                if account.currency_id.id == son.currency_id.id \
                        or field == 'quantity':
                    account[field] += son[field]
                else:
                    account[field] += currency_obj.compute(
                        son.currency_id.id,
                        account.currency_id.id, son[field]
                    )
        return True

    def _compute_level_tree(self, child_ids, field_names):
        for account in self:
            if account.id not in child_ids:
                continue
            self.recursive_computation(account.id, field_names)
        return True

    @api.multi
    def _debit_credit_bal_qtty(self):
        field_names = ['debit', 'credit', 'balance', 'quantity']
        children = tuple(self.search([('parent_id', 'child_of', self._ids)]))
        child_ids = []
        for child in children:
            child_ids.append(child.id)
            for name in field_names:
                child[name] = 0.0

        if not children:
            return

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if self._context.get('from_date', False):
            where_date += ' AND l.date >= %s'
            where_clause_args += [self._context['from_date']]
        if self._context.get('to_date', False):
            where_date += ' AND l.date <= %s'
            where_clause_args += [self._context['to_date']]
        self.env.cr.execute("""
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
              GROUP BY a.id
              """, where_clause_args)
        for ac_id, debit, credit, balance, quantity in self.env.cr.fetchall():
            current_account = self.browse(ac_id)
            current_account.debit = debit
            current_account.credit = credit
            current_account.balance = balance
            current_account.quantity = quantity

        return self._compute_level_tree(child_ids, field_names)

    def _default_company(self):
        user = self.env['res.users'].browse(self._uid)
        if user.company_id:
            return user.company_id.id
        companies = self.env['res.company'].search([('parent_id', '=', False)])
        if companies:
            return companies[0].id
        return False

    def _get_default_currency(self):
        user = self.env['res.users'].browse(self._uid)
        if user and user.company_id and user.company_id.currency_id:
            return user.company_id.currency_id.id
        return False

    def _get_default_date(self):
        return fields.Date.context_today(self)

    @api.one
    @api.depends('name', 'code')
    def _compute_display_name(self):
        self.display_name = '[%s] %s' % (self.code, self.name)

    code = fields.Char(
        string='Code',
        required=True,
        size=64
    )
    name = fields.Char(
        string='Activity',
        required=True,
        size=64,
        translate=True
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
    )
    parent_id = fields.Many2one(
        comodel_name='project.activity_al',
        string='Parent activity'
    )
    project_ids = fields.Many2many(
        comodel_name='account.analytic.account',
        relation='proj_activity_analytic_rel',
        column1='activity_id',
        column2='analytic_id',
        string='Concerned Analytic Account'
    )
    child_ids = fields.One2many(
        comodel_name='project.activity_al',
        inverse_name='parent_id',
        string='Child Activities'
    )
    balance = fields.Float(
        string='Balance',
        digits_compute=dp.get_precision('Account'),
        compute='_debit_credit_bal_qtty'
    )
    debit = fields.Float(
        string='Debit',
        digits_compute=dp.get_precision('Account'),
        compute='_debit_credit_bal_qtty'
    )
    credit = fields.Float(
        string='Credit',
        digits_compute=dp.get_precision('Account'),
        compute='_debit_credit_bal_qtty'
    )
    quantity = fields.Float(
        string='Quantity',
        digits_compute=dp.get_precision('Account'),
        compute='_debit_credit_bal_qtty'
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Activity currency',
        required=True,
        default='_get_default_currency'
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=False,
        default='_default_company'
    )
    date = fields.Date(
        string='Date',
        required=False,
        default='_get_default_date'
    )


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    activity_ids = fields.Many2many(
        comodel_name='project.activity_al',
        relation='proj_activity_analytic_rel',
        column1='analytic_id',
        column2='activity_id',
        string='Related activities'
    )


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    activity = fields.Many2one(
        comodel_name='project.activity_al',
        string='Activity'
    )
