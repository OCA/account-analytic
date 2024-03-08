# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
        sol_id = move_values.get("sale_line_id", False)
        if sol_id:
            sol_model = self.env["sale.order.line"]
            sol = sol_model.browse(sol_id)
            analytic_tags = sol.analytic_tag_ids
            analytic_account = sol.order_id.analytic_account_id
            if analytic_tags:
                move_values.update({"analytic_tag_ids": [(6, 0, analytic_tags.ids)]})
            if analytic_account:
                move_values.update({"analytic_account_id": analytic_account.id})
        return move_values
