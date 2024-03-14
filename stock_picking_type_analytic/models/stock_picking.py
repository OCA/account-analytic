# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.model
    def create(self, vals):
        """
        Get analytic account from picking type if set
        """
        defaults = self.default_get(["name", "picking_type_id"])
        picking_type = self.env["stock.picking.type"].browse(
            vals.get("picking_type_id", defaults.get("picking_type_id"))
        )
        if "analytic_account_id" not in vals and picking_type.analytic_account_id:
            vals.update(
                {
                    "original_analytic_account_id": picking_type.analytic_account_id.id,
                }
            )
        return super().create(vals)

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id_analytic(self):
        for picking in self:
            if (
                picking.picking_type_id
                and picking.picking_type_id.analytic_account_id
                and not picking.analytic_account_id
            ):
                picking.analytic_account_id = (
                    picking.picking_type_id.analytic_account_id
                )
