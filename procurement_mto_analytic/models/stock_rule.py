# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        res = super()._make_po_get_domain(company_id, values, partner)
        if values.get("analytic_distribution", False):
            res += (
                (
                    "order_line.analytic_distribution",
                    "=",
                    json.dumps(values.get("analytic_distribution")),
                ),
            )
        return res
