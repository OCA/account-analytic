from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        for move in moves.filtered(
            lambda m: (
                m.maintenance_equipment_id
                and not m.analytic_distribution
                and m.maintenance_equipment_id.analytic_distribution
            )
        ):
            move.analytic_distribution = (
                move.maintenance_equipment_id.analytic_distribution
            )
        return moves
