from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends("picking_id.maintenance_request_id")
    def _compute_analytic_distribution(self):
        res = super()._compute_analytic_distribution()
        for move in self:
            equipment = move.picking_id.maintenance_request_id.equipment_id
            if equipment and equipment.analytic_distribution:
                move.analytic_distribution = equipment.analytic_distribution
            return res
