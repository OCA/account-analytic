# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.fields import first


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    group_id = fields.Many2one("procurement.group")

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
        line = super()._find_candidate(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        analytic_id = values.get("analytic_account_id")
        if analytic_id:
            line_candidates = self.filtered(
                lambda line: line.account_analytic_id.id == analytic_id
            )
            if line_candidates:
                return first(line_candidates)
        return line

    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        analytic_id = values.get("analytic_account_id")
        if analytic_id:
            res.update(
                {
                    "account_analytic_id": analytic_id,
                }
            )
        return res
