# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tools import config
from odoo import api, fields, models


class AccountAnalyticDefaultAccount(models.Model):
    _inherit = "account.analytic.default"

    account_id = fields.Many2one(
        'account.account', string='Account',
        ondelete='cascade',
        help="Select the account corresponding to an analytic account "
             "which will be used on the lines of invoices or account moves"
    )

    def _account_get_domain(self, **kw):
        """Build account.analytic.default domain.

        :param kw: filter keys.
            Available filter keys are defined into `account_get_domain_keys`.
        :return: a search domain with all required keys' leaves.
            Each key will be searched for both False and specified value.
            For instance: [
                ('product_id'), '=', False), '|', [('product_id'), '=', 100)
            ]
        """
        domain = []
        # date will be handled differently
        date_val = kw.pop('date')

        for key, value in kw.items():
            if value:
                domain += ['|', (key, '=', kw.get(key))]
            domain += [(key, '=', False)]

        if date_val:
            domain += ['|', ('date_start', '<=', date_val),
                       ('date_start', '=', False)]
            domain += ['|', ('date_stop', '>=', date_val),
                       ('date_stop', '=', False)]
        return domain

    @api.model
    def account_get(self, product_id=None, partner_id=None, user_id=None,
                    date=None, company_id=None, account_id=None):
        """Search the records matching the built domain,
        compute an index score based on the actual record values then
        return the record with the highest index score"""
        filters = {
            'product_id': product_id,
            'partner_id': partner_id,
            'user_id': user_id,
            'date': date,
            'company_id': company_id,
            'account_id': account_id,
        }
        domain = self._account_get_domain(**filters)
        keys = list(filters)
        if 'date' in keys:
            keys.remove('date')
            keys += ['date_start', 'date_stop']
        best_index = -1
        res = self.env['account.analytic.default']
        for rec in self.search(domain):
            index = 0
            for k in keys:
                if rec[k]:
                    index += 1
            if index > best_index:
                res = rec
                best_index = index
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id', 'account_id')
    def _onchange_product_id(self):
        res = super()._onchange_product_id()
        if (not config['test_enable'] or
                self.env.context.get('test_account_analytic_default_account')):
            rec = self.env['account.analytic.default'].account_get(
                product_id=self.product_id.id,
                partner_id=self.invoice_id.partner_id.id,
                user_id=self.env.uid, date=fields.Date.today(),
                company_id=self.company_id.id, account_id=self.account_id.id
            )
            self.account_analytic_id = rec.analytic_id.id
        return res

    def _set_additional_fields(self, invoice):
        if not self.account_analytic_id:
            rec = self.env['account.analytic.default'].account_get(
                product_id=self.product_id.id,
                partner_id=self.invoice_id.partner_id.id,
                user_id=self.env.uid, date=fields.Date.today(),
                company_id=self.company_id.id, account_id=self.account_id.id
            )
            if rec:
                self.account_analytic_id = rec.analytic_id.id
        super()._set_additional_fields(invoice)


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
        return super().create(vals)


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def post(self):
        self.mapped('line_ids')._set_default_analytic_account()
        return super().post()
