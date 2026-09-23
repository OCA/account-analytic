# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            is_raw = vals.get("raw_material_production_id")
            is_finished = vals.get("production_id")
            production_id = is_raw or is_finished
            if not production_id or vals.get("analytic_distribution"):
                continue
            production = self.env["mrp.production"].browse(production_id)
            if not production.analytic_distribution:
                continue
            if is_raw or (
                is_finished and production.company_id.mrp_analytic_on_finished
            ):
                vals["analytic_distribution"] = production.analytic_distribution
        return super().create(vals_list)
