# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        for move in self:
            # Validate analytic distribution for receipts.
            if move.picking_type_id.code == "incoming":
                move._validate_distribution(
                    **{
                        "product": move.product_id.id,
                        "business_domain": "stock_move",
                        "company_id": move.company_id.id,
                    }
                )
        return super()._action_done(cancel_backorder=cancel_backorder)
