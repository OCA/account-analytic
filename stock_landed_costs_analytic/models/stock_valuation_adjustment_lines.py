# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockValuationAdjustmentLines(models.Model):
    _name = "stock.valuation.adjustment.lines"
    _inherit = ["stock.valuation.adjustment.lines", "analytic.mixin"]

    def _create_account_move_line(
        self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id
    ):
        res = super()._create_account_move_line(
            move, credit_account_id, debit_account_id, qty_out, already_out_account_id
        )
        cost_line = self.cost_line_id
        for line in res:
            if line[2]["account_id"] == cost_line.account_id.id:
                if cost_line.analytic_distribution:
                    line[2].update(
                        {"analytic_distribution": cost_line.analytic_distribution}
                    )
        return res
