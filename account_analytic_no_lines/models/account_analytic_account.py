# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    @api.multi
    def _compute_gl_debit_credit_balance(self):
        aml_obj = self.env['account.move.line']
        domain = [('analytic_account_id', 'in', self.ids)]
        if self._context.get('from_date'):
            domain.append(('date', '>=', self._context['from_date']))
        if self._context.get('to_date'):
            domain.append(('date', '<=', self._context['to_date']))

        amounts = aml_obj.read_group(
            domain,
            ['analytic_account_id', 'debit', 'credit', 'balance'],
            ['analytic_account_id'])

        amount_by_aa = {
            amount['analytic_account_id'][0]: amount
            for amount in amounts
        }

        for rec in self:
            rec.gl_debit = amount_by_aa.get(rec.id, {}).get('debit', 0.0)
            rec.gl_credit = amount_by_aa.get(rec.id, {}).get('credit', 0.0)
            rec.gl_balance = -amount_by_aa.get(rec.id, {}).get('balance', 0.0)

    gl_debit = fields.Monetary(
        compute='_compute_gl_debit_credit_balance',
        string='Debit (GL)',
    )
    gl_credit = fields.Monetary(
        compute='_compute_gl_debit_credit_balance',
        string='Credit (GL)',
    )
    gl_balance = fields.Monetary(
        compute='_compute_gl_debit_credit_balance',
        string='Analytic Balance (GL)',
        help="Credit - Debit",
    )
