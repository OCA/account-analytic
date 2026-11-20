# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventoryAdjustmentName(models.TransientModel):
    _inherit = "stock.inventory.adjustment.name"

    def _get_default_analytic_distribution(self):
        return self.env.company.analytic_distribution

    def _get_default_analytic_precision(self):
        return self.env.company.analytic_precision

    analytic_distribution = fields.Json(
        default=lambda self: self._get_default_analytic_distribution()
    )
    analytic_precision = fields.Integer(
        default=lambda self: self._get_default_analytic_precision()
    )

    def _get_quants_context(self):
        ctx = super()._get_quants_context()
        if self.analytic_distribution:
            ctx["analytic_distribution"] = self.analytic_distribution
        return ctx
