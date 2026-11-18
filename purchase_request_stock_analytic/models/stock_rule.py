# Copyright 2026 Scalizer (https://www.scalizer.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _prepare_purchase_request_line(self, request_id, procurement):
        """Copy the analytic distribution of the procurement on the line.

        The distribution is set in the procurement values by ``stock_analytic``
        from the stock move at the origin of the need.
        """
        vals = super()._prepare_purchase_request_line(request_id, procurement)
        analytic_distribution = procurement.values.get("analytic_distribution")
        if analytic_distribution:
            vals["analytic_distribution"] = analytic_distribution
        return vals
