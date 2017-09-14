# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier)
        res['account_analytic_id'] = self.account_analytic_id.id
        return res

    @api.multi
    def make_po(self):
        # This is a trick to avoid the grouping without this key.
        obj = self.with_context(
            limit_procurement_account_analytic_id=self.account_analytic_id.id)
        return super(ProcurementOrder, obj).make_po()
