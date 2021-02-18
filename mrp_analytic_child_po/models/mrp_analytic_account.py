# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for order in self:
            stock_move_ids = order.procurement_group_id.stock_move_ids
            purchase_orders = (
                stock_move_ids.created_purchase_line_id.order_id
                | stock_move_ids.move_orig_ids.purchase_line_id.order_id
            )
            for purchase in purchase_orders:
                for line in purchase.order_line:
                    line.account_analytic_id = (
                        order.analytic_account_id.id
                        if order.analytic_account_id
                        else None
                    )

        return res
