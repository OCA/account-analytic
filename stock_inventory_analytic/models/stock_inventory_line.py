# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        default=lambda self: self.env.user.company_id.analytic_account_id.id,
    )
    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag",
        string="Analytic Tags",
        default=lambda self: self.env.user.company_id.analytic_tag_ids.ids,
    )

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super(StockInventoryLine, self)._get_move_values(
            qty, location_id, location_dest_id, out
        )
        if self.analytic_account_id:
            res["analytic_account_id"] = self.analytic_account_id.id
        if self.analytic_tag_ids:
            res["analytic_tag_ids"] = [(6, 0, self.analytic_tag_ids.ids)]
        return res
