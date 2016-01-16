# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# © 2016 Antiun Ingeniería S.L. - Javier Iniesta
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(
            self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False,
            currency_id=False, company_id=None):
        res = super(AccountInvoiceLine, self).product_id_change(
            product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit,
            currency_id=currency_id, company_id=company_id)
        if company_id is None:
            company_id = self._context.get('company_id', False)
        self = self.with_context(
            company_id=company_id, force_company=company_id)
        if product:
            product_o = self.env['product.product'].browse(product)
            account_analytic_id = False
            if type in ('out_invoice', 'out_refund'):
                account_analytic_id =\
                    product_o.income_analytic_account_id.id or\
                    product_o.categ_id.income_analytic_account_id.id
            else:
                account_analytic_id =\
                    product_o.expense_analytic_account_id.id or\
                    product_o.categ_id.expense_analytic_account_id.id
            if account_analytic_id:
                res['value']['account_analytic_id'] = account_analytic_id
        return res

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
