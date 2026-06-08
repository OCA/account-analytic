# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_stock_move_values(
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
        res = super()._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        if values.get("stock_request_id"):
            stock_request = self.env["stock.request"].browse(values["stock_request_id"])
            analytic_tags = stock_request.analytic_tag_ids
            if analytic_tags:
                res.update(analytic_tag_ids=[(4, tag.id) for tag in analytic_tags])
        return res
