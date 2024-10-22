# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    def _inverse_analytic_distribution(self):
        for move in self:
            if not move.is_subcontract:
                continue
            production = self.search(
                [
                    ("product_id", "=", move.product_id.id),
                    ("move_dest_ids", "=", move.id),
                ]
            ).production_id
            if production:
                production.analytic_distribution = move.analytic_distribution
