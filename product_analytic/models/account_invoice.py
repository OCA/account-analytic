# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (http://www.akretion.com/) - Alexis de Lattre
# © 2016 Antiun Ingeniería S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def product_analytic_change(self):
        if self.product_id:
            account_analytic = False
            if self.invoice_id.type in ('out_invoice', 'out_refund'):
                account_analytic =\
                    self.product_id.income_analytic_account_id or\
                    self.product_id.categ_id.income_analytic_account_id
            else:
                account_analytic =\
                    self.product_id.expense_analytic_account_id or\
                    self.product_id.categ_id.expense_analytic_account_id
            if account_analytic:
                self.account_analytic_id = account_analytic

    @api.model
    def create(self, vals):
        type = self.env.context.get('inv_type', 'out_invoice')
        if vals.get('product_id') and type and \
                not vals.get('account_analytic_id'):
            product = self.env['product.product'].browse(
                vals.get('product_id'))
            if type in ('out_invoice', 'out_refund'):
                analytic_id = product.income_analytic_account_id.id or\
                    product.categ_id.income_analytic_account_id.id
            else:
                analytic_id = product.expense_analytic_account_id.id or\
                    product.categ_id.expense_analytic_account_id.id
            if analytic_id:
                vals['account_analytic_id'] = analytic_id
        return super(AccountInvoiceLine, self).create(vals)
