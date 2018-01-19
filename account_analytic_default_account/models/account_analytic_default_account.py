# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class AccountAnalyticDefaultAccount(models.Model):
    _inherit = "account.analytic.default"

    account_id = fields.Many2one(
        'account.account', string='Account',
        ondelete='cascade',
        help="Select an account which will use analytic account specified in "
             "analytic default (e.g. create new customer invoice or "
             "Sales order if we select this product, "
             "it will automatically take this as an analytic account)"
    )

    @api.model
    def account_get(self, product_id=None, partner_id=None, user_id=None,
                    date=None, company_id=None, account_id=None):
        domain = []
        if product_id:
            domain += ['|', ('product_id', '=', product_id)]
        domain += [('product_id', '=', False)]
        if partner_id:
            domain += ['|', ('partner_id', '=', partner_id)]
        domain += [('partner_id', '=', False)]
        if company_id:
            domain += ['|', ('company_id', '=', company_id)]
        domain += [('company_id', '=', False)]
        if user_id:
            domain += ['|', ('user_id', '=', user_id)]
        domain += [('user_id', '=', False)]
        if account_id:
            domain += ['|', ('account_id', '=', account_id)]
        domain += [('account_id', '=', False)]
        if date:
            domain += ['|', ('date_start', '<=', date),
                       ('date_start', '=', False)]
            domain += ['|', ('date_stop', '>=', date),
                       ('date_stop', '=', False)]
        best_index = -1
        res = self.env['account.analytic.default']
        for rec in self.search(domain):
            index = 0
            if rec.product_id:
                index += 1
            if rec.partner_id:
                index += 1
            if rec.company_id:
                index += 1
            if rec.user_id:
                index += 1
            if rec.account_id:
                index += 1
            if rec.date_start:
                index += 1
            if rec.date_stop:
                index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        rec = self.env['account.analytic.default'].account_get(
            self.product_id.id, self.invoice_id.partner_id.id, self.env.uid,
            fields.Date.today(), company_id=self.company_id.id,
            account_id=self.account_id.id)
        self.account_analytic_id = rec.analytic_id.id
        return res

    def _set_additional_fields(self, invoice):
        if not self.account_analytic_id:
            rec = self.env['account.analytic.default'].account_get(
                self.product_id.id, self.invoice_id.partner_id.id,
                self.env.uid, fields.Date.today(),
                company_id=self.company_id.id, account_id=self.account_id.id
            )
            if rec:
                self.account_analytic_id = rec.analytic_id.id
        super(AccountInvoiceLine, self)._set_additional_fields(invoice)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('account_id')
    def _onchange_account_id(self):
        for line in self:
            if line.account_id and not line.analytic_account_id:
                rec = self.env['account.analytic.default'].account_get(
                    account_id=line.account_id.id)
                if rec:
                    line.analytic_account_id = rec.analytic_id.id

    @api.multi
    def _set_default_analytic_account(self):
        for line in self:
            if not line.analytic_account_id:
                rec = self.env['account.analytic.default'].account_get(
                    account_id=line.account_id.id)
                if rec:
                    line.analytic_account_id = rec.analytic_id.id

    @api.model
    def create(self, vals):
        if 'analytic_account_id' not in vals:
            rec = self.env['account.analytic.default'].account_get(
                account_id=vals.get('account_id'))
            if rec:
                vals['analytic_account_id'] = rec.analytic_id.id
        return super(AccountMoveLine, self).create(vals)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        self.mapped('line_ids')._set_default_analytic_account()
        return super(AccountMove, self).post()
