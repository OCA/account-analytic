# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        res = super()._make_po_get_domain(company_id, values, partner)
        res += (
            (
                "order_line.account_analytic_id",
                "=",
                values.get("account_analytic_id", False),
            ),
        )
        return res
