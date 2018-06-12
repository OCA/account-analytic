# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):

    _inherit = 'purchase.order.line'

    @api.multi
    def _create_stock_moves(self, picking):
        moves = super(PurchaseOrderLine, self)._create_stock_moves(
            picking=picking)
        for move in moves.filtered(lambda m: not m.analytic_account_id):
            move.write({
                'analytic_account_id':
                    move.purchase_line_id.account_analytic_id.id
            })
        return moves
