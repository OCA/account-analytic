# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    @api.model
    def create(self, vals):
        # Scrap from picking
        picking_id = vals.get("picking_id", False)
        if picking_id:
            product_id = vals.get("product_id", False)
            move = self.env["stock.move"].search(
                [("picking_id", "=", picking_id), ("product_id", "=", product_id)],
                limit=1,
            )
            vals["analytic_account_id"] = move.analytic_account_id.id
        # Scrap from production
        production_id = vals.get("production_id", False)
        if production_id:
            production = self.env["mrp.production"].browse(production_id)
            vals["analytic_account_id"] = production.analytic_account_id.id
        return super().create(vals)
