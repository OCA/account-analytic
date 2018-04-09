# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        ana_accounts = self.product_id.product_tmpl_id.\
            _get_product_analytic_accounts()
        ana_account = ana_accounts['income']
        vals['account_analytic_id'] = ana_account.id or False
        return vals
