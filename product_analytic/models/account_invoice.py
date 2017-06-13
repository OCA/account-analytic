# -*- coding: utf-8 -*-
# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        type = self.invoice_id.type
        product = self.product_id
        if product:
            if type in ('out_invoice', 'out_refund'):
                self.account_analytic_id =\
                    product.income_analytic_account_id.id or\
                    product.categ_id.income_analytic_account_id.id
            else:
                self.account_analytic_id =\
                    product.expense_analytic_account_id.id or\
                    product.categ_id.expense_analytic_account_id.id
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
