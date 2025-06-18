# Copyright 2025 Bernat Obrador APSL-Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)

        stock_analytic_model = self.env["stock.analytic.rule"].sudo()
        for move_id in res:
            if move_id.state == "done":
                stock_analytic_model.generate_analytic_lines(move_id)
        return res

    def write(self, vals):
        res = super().write(vals)

        for record in self:
            # Look if this move has analytic lines
            analytic_lines = analytic_lines = (
                self.env["account.analytic.line"]
                .sudo()
                .search([("stock_move_id", "=", record.id)])
                if record.id
                else False
            )

            stock_analytic_model = self.env["stock.analytic.rule"].sudo()

            if vals.get("state") == "done" and not analytic_lines:
                stock_analytic_model.generate_analytic_lines(record)

            if analytic_lines:
                analytic_lines.unlink()
                stock_analytic_model.generate_analytic_lines(record)

        return res
