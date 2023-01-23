# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
        move_values = super(StockRule, self)._get_stock_move_values(
            product_id,
            product_qty,
            product_uom,
            location_id,
            name,
            origin,
            company_id,
            values,
        )
        sale_line_id = move_values.get("sale_line_id", False)
        if sale_line_id:
            sale_line = self.env["sale.order.line"].browse(sale_line_id)
            analytic_tags = sale_line.analytic_tag_ids
            analytic_account = sale_line.analytic_account_id
            if analytic_tags:
                move_values.update({"analytic_tag_ids": [(6, 0, analytic_tags.ids)]})
            if analytic_account:
                move_values.update({"analytic_account_id": analytic_account.id})
        return move_values
