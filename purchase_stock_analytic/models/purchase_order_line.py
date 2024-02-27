# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, values):
        res = super().write(values)
        if "analytic_distribution" in values:
            for line in self:
                moves = line.move_ids.filtered(
                    lambda s: s.state not in ("cancel", "done")
                    and s.product_id == line.product_id
                )
                moves.write({"analytic_distribution": line.analytic_distribution})
        return res

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        if not self.analytic_distribution:
            return res
        for line in res:
            line.update({"analytic_distribution": self.analytic_distribution})
        return res
