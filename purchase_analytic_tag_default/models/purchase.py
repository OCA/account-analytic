# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields, api


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        rec = self.env['account.analytic.default'].account_get(
            self.product_id.id, self.order_id.partner_id.id, self.env.uid,
            fields.Date.today(), company_id=self.order_id.company_id.id)
        if rec:
            if rec.analytic_id:
                self.account_analytic_id = rec.analytic_id.id
            if rec.analytic_tag_ids:
                self.analytic_tag_ids = rec.analytic_tag_ids.ids
        return
