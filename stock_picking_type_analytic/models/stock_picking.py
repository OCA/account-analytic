# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model_create_multi
    def create(self, vals_list):
        """
        Get analytic distribution from picking type if set
        """
        defaults = self.default_get(["name", "picking_type_id"])
        for vals in vals_list:
            picking_type = self.env["stock.picking.type"].browse(
                vals.get("picking_type_id", defaults.get("picking_type_id"))
            )
            if (
                "analytic_distribution" not in vals
                and picking_type.analytic_distribution
            ):
                vals.update(
                    {
                        "original_analytic_distribution": (
                            picking_type.analytic_distribution
                        ),
                    }
                )
        return super().create(vals_list)

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id_analytic(self):
        for picking in self:
            if (
                picking.picking_type_id
                and picking.picking_type_id.analytic_distribution
                and not picking.analytic_distribution
            ):
                picking.analytic_distribution = (
                    picking.picking_type_id.analytic_distribution
                )
