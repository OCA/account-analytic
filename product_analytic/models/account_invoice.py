# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

INV_TYPE_MAP = {
    'out_invoice': 'income',
    'out_refund': 'income',
    'in_invoice': 'expense',
    'in_refund': 'expense',
}


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        inv_type = self.invoice_id.type
        if self.product_id:
            ana_accounts = self.product_id.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
            self.account_analytic_id = ana_account.id
        return res

    @api.model
    def create(self, vals):
        inv_type = self.env.context.get('inv_type', 'out_invoice')
        if vals.get('product_id') and inv_type and \
                not vals.get('account_analytic_id'):
            product = self.env['product.product'].browse(
                vals.get('product_id'))
            ana_accounts = product.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[inv_type]]
            vals['account_analytic_id'] = ana_account.id
        return super(AccountInvoiceLine, self).create(vals)
