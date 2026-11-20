# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = "stock.inventory.adjustment.name"

    def _get_default_analytic_distribution(self):
        location_id = self.env.context.get("default_location_id")
        location = self.env["stock.location"].browse(location_id)
        if location.warehouse_id.analytic_distribution:
            return location.warehouse_id.analytic_distribution
        return super()._get_default_analytic_distribution()

    def _get_default_analytic_precision(self):
        location_id = self.env.context.get("default_location_id")
        location = self.env["stock.location"].browse(location_id)
        if location.warehouse_id.analytic_precision:
            return location.warehouse_id.analytic_precision
        return super()._get_default_analytic_precision()
