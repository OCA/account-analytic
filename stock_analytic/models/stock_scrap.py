# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class StockScrap(models.Model):
    _name = "stock.scrap"
    _inherit = ["stock.scrap", "analytic.mixin"]

    def _prepare_move_values(self):
        res = super()._prepare_move_values()
        res.update(
            {
                "analytic_distribution": self.analytic_distribution,
            }
        )
        return res

    def action_validate(self):
        self = self.with_context(validate_analytic=True)
        return super().action_validate()
