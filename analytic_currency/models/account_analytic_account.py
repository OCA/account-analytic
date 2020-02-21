# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related=None,
        readonly=False,
        required=True,
        default=lambda self: self._get_default_currency_id(),
        track_visibility='onchange',
    )
    user_currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_user_currency_id',
    )
    balance = fields.Monetary(
        currency_field='user_currency_id',
    )
    debit = fields.Monetary(
        currency_field='user_currency_id',
    )
    credit = fields.Monetary(
        currency_field='user_currency_id',
    )
    original_balance = fields.Monetary(
        string='Balance (original)',
        compute='_compute_original_debit_credit_balance',
    )
    original_debit = fields.Monetary(
        string='Debit (original)',
        compute='_compute_original_debit_credit_balance',
    )
    original_credit = fields.Monetary(
        string='Credit (original)',
        compute='_compute_original_debit_credit_balance',
    )

    def _get_default_currency_id(self):
        return self.company_id.currency_id \
            or self.env.user.company_id.currency_id

    @api.multi
    def _compute_user_currency_id(self):
        for aaa in self:
            aaa.user_currency_id = self.env.user.company_id.currency_id

    @api.multi
    @api.depends('line_ids.amount', 'currency_id', 'company_id')
    def _compute_original_debit_credit_balance(self):
        AccountAnalyticLine = self.env['account.analytic.line']
        ResCurrency = self.env['res.currency']
        today = fields.Date.today()
        context_domain = []
        if self.env.context.get('from_date', False):
            context_domain += [('date', '>=', self.env.context['from_date'])]
        if self.env.context.get('to_date', False):
            context_domain += [('date', '<=', self.env.context['to_date'])]
        if self.env.context.get('tag_ids'):
            tag_domain = expression.OR([
                [('tag_ids', 'in', [tag])]
                for tag in self.env.context['tag_ids']
            ])
            context_domain = expression.AND([context_domain, tag_domain])
        if self.env.context.get('company_ids'):
            context_domain += [
                ('company_id', 'in', self.env.context['company_ids'])
            ]

        for aaa in self:
            if self._parent_store:
                domain = context_domain + [('account_id', 'child_of', aaa.id)]
            else:
                domain = context_domain + [('account_id', '=', aaa.id)]

            credit_groups = AccountAnalyticLine.read_group(
                domain=domain + [('amount', '>=', 0.0)],
                fields=['currency_id', 'amount'],
                groupby=['currency_id'],
                lazy=False,
            )
            original_credit = 0.0
            for group in credit_groups:
                aal_currency = ResCurrency.browse(group['currency_id'][0])
                original_credit += aal_currency._convert(
                    group['amount'],
                    aaa.currency_id,
                    aaa.company_id,
                    today
                )

            debit_groups = AccountAnalyticLine.read_group(
                domain=domain + [('amount', '<', 0.0)],
                fields=['currency_id', 'amount'],
                groupby=['currency_id'],
                lazy=False,
            )
            original_debit = 0.0
            for group in debit_groups:
                aal_currency = ResCurrency.browse(group['currency_id'][0])
                original_debit -= aal_currency._convert(
                    group['amount'],
                    aaa.currency_id,
                    aaa.company_id,
                    today
                )

            aaa.original_debit = original_debit
            aaa.original_credit = original_credit
            aaa.original_balance = original_credit - original_debit

    @api.multi
    def write(self, vals):
        if 'currency_id' in vals \
                and not self.user_has_groups('base.group_no_one') \
                and self.filtered('line_ids'):
            currency = self.env['res.currency'].browse(
                vals['currency_id']
            )
            existing_lines = self.filtered(
                lambda account: account.currency_id != currency
            ).mapped('line_ids').filtered(lambda aal: aal.amount != 0)
            if existing_lines:
                raise UserError(_(
                    'Changing currency on a Analytic Account with existing'
                    ' lines is not going to convert amounts and is likely to'
                    ' make data meaningful! Yet if you do need to do that, use'
                    ' Developer Mode to bypass the safeguard.'
                ))
        return super().write(vals)

    @api.model
    def fields_view_get(self,
                        view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )

        if view_type == 'tree':
            currency = self.env.user.company_id.currency_id
            view = etree.XML(res['arch'])

            debit_field = view.find(".//field[@name='debit']")
            if debit_field is not None:
                debit_field.set('string', _('Debit\u00A0(%s)') % (
                    currency.name,
                ))

            credit_field = view.find(".//field[@name='credit']")
            if credit_field is not None:
                credit_field.set('string', _('Credit\u00A0(%s)') % (
                    currency.name,
                ))

            balance_field = view.find(".//field[@name='balance']")
            if balance_field is not None:
                balance_field.set('string', _('Balance\u00A0(%s)') % (
                    currency.name,
                ))

            res['arch'] = etree.tostring(
                view,
                encoding='unicode',
            ).replace('\t', '')

        return res
