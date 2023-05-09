# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_value_production_lot(self):
        self.ensure_one()
        res = super()._get_value_production_lot()
        res.update(
            {
                "analytic_distribution": self.move_id.analytic_distribution,
            }
        )
        return res
