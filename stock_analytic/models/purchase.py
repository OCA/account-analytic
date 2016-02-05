# -*- coding: utf-8 -*-
# © 2013 Julius Network Solutions
# © 2015 Clear Corp
# © 2016 Andhitia Rama <andhitia.r@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def _prepare_order_line_move(self, order, order_line,
                                 picking_id, group_id, context=None):
        res = super(
            PurchaseOrder, self)._prepare_order_line_move(
                self.env.cr, self.user.id,
                order, order_line, picking_id, group_id,
                context=context)
        if order_line.account_analytic_id:
            for move in res:
                move['account_analytic_id'] = order_line.account_analytic_id.id
        return res
