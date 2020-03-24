# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update(
            {"account_analytic_id": self.group_id.sale_id.analytic_account_id.id}
        )
        return res
