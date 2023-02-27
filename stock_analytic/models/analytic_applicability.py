# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticApplicability(models.Model):
    _inherit = "account.analytic.applicability"

    business_domain = fields.Selection(
        selection_add=[("stock_move", "Stock Move")],
        ondelete={"stock_move": "cascade"},
    )
    stock_picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Operation Type",
    )

    def _get_score(self, **kwargs):
        score = super()._get_score(**kwargs)
        if score >= 0 and self.stock_picking_type_id:
            if kwargs.get("picking_type") == self.stock_picking_type_id.id:
                score += 1
            else:
                return -1
        return score
