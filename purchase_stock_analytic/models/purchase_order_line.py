# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for line in res:
            analytic_distribution = self.analytic_distribution
            if analytic_distribution:
                line.update({"analytic_distribution": analytic_distribution})
        return res
