# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        rec = self.env['account.analytic.default'].account_get(
            self.product_id.id, self.order_id.partner_id.id, self.env.uid,
            fields.Date.today(), company_id=self.order_id.company_id.id)
        if rec and rec.analytic_tag_ids:
            self.analytic_tag_ids = rec.analytic_tag_ids.ids
        return

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        if not self.analytic_tag_ids:
            rec = self.env['account.analytic.default'].account_get(
                self.product_id.id, self.order_id.partner_id.id,
                self.order_id.user_id.id, fields.Date.today())
            if rec and rec.analytic_tag_ids:
                res['analytic_tag_ids'] = [(6, False,
                                            rec.analytic_tag_ids.ids)]
        return res
