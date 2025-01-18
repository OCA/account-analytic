# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    @api.returns("self")
    def search(self, domain, offset=0, limit=None, order=None):
        new_domain = []
        for element in domain:
            if element[0] == "order_line.analytic_distribution":
                try:
                    value = json.loads(element[2])
                except json.JSONDecodeError:
                    new_domain.append(element)
                new_domain.append(
                    (
                        "order_line.analytic_distribution",
                        "=",
                        value,
                    )
                )
            else:
                new_domain.append(element)
        return super().search(new_domain, offset=offset, limit=limit, order=order)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if values.get("analytic_distribution", False):
            res["analytic_distribution"] = values.get("analytic_distribution", False)
        return res
