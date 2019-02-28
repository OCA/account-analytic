# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super(
            PurchaseOrderLine, self
        )._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        res["account_analytic_id"] = values.get("account_analytic_id", False)

        return res

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        """
        This function's purpose is to be overriden with the purpose to
        forbid _run_buy  method to merge a new po line in an existing one.
        Purchase lines should not be merged if they were procured by sale
        lines with different analytic account.
        """

        account_analytic_id = values.get("account_analytic_id", False)
        lines = self.filtered(
            lambda line: line.account_analytic_id.id == account_analytic_id
        )

        res = super(PurchaseOrderLine, lines)._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )

        return res
