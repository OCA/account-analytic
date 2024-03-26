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
        res["analytic_distribution"] = values.get("analytic_distribution", False)
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
        lines = (
            self.filtered(
                lambda po_line: po_line.analytic_distribution
                == values["analytic_distribution"]
            )
            if values.get("analytic_distribution")
            else self
        )
        return super(PurchaseOrderLine, lines)._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
