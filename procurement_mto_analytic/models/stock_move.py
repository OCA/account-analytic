# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        analytic_distribution = self.sale_line_id.analytic_distribution
        # In case of using stock_analytic and mrp_stock_analytic
        if not analytic_distribution and hasattr(self, "analytic_distribution"):
            analytic_distribution = self.analytic_distribution
        # Update the procurement values with analytic_distribution if it exists
        if analytic_distribution:
            res.update({"analytic_distribution": analytic_distribution})
        return res
