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

    def _make_po_get_domain(self, partner):
        res = super(ProcurementOrder, self)._make_po_get_domain(
            partner=partner)
        res += (('order_line.account_analytic_id',
                 '=', self.account_analytic_id.id),)
        return res
