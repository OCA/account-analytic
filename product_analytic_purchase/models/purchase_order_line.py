# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            ana_accounts = self.product_id.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts['expense']
            self.account_analytic_id = ana_account.id
        return res

    @api.model
    def create(self, vals):
        if vals.get('product_id') and not vals.get('account_analytic_id'):
            product = self.env['product.product'].browse(
                vals.get('product_id'))
            ana_accounts = product.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts['expense']
            vals['account_analytic_id'] = ana_account.id
        return super(PurchaseOrderLine, self).create(vals)
