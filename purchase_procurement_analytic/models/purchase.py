# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def search(self, args, offset=0, limit=None, order=None, count=False):
        if 'limit_procurement_account_analytic_id' in self.env.context:
            args.insert(0, ('account_analytic_id', '=', self.env.context.get(
                'limit_procurement_account_analytic_id')))
        return super(PurchaseOrderLine, self).search(
            args, offset=offset, limit=limit, order=order, count=count)
