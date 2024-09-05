from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Extend to copy the analytic distribution of the manufacturing order
        if a move is added as a raw material move to it.
        """
        for vals in vals_list:
            if "analytic_distribution" in vals:
                continue
            raw_production = (
                self.env["mrp.production"]
                .browse(vals.get("raw_material_production_id"))
                .exists()
            )
            if not raw_production.analytic_distribution:
                continue
            vals["analytic_distribution"] = raw_production.analytic_distribution
        return super().create(vals_list)
