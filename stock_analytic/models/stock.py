# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 ForgeFlow S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "analytic.mixin"]

    def _prepare_account_move_line(
        self, qty, cost, credit_account_id, debit_account_id, svl_id, description
    ):
        self.ensure_one()
        res = super()._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, svl_id, description
        )
        if not self.analytic_distribution:
            return res
        for line in res:
            if (
                line[2]["account_id"]
                != self.product_id.categ_id.property_stock_valuation_account_id.id
            ):
                # Add analytic account in debit line
                line[2].update({"analytic_distribution": self.analytic_distribution})
        return res

    def _prepare_procurement_values(self):
        """
        Allows to transmit analytic account from moves to new
        moves through procurement.
        """
        res = super()._prepare_procurement_values()
        if self.analytic_distribution:
            res.update(
                {
                    "analytic_distribution": self.analytic_distribution,
                }
            )
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        """
        We fill in the analytic account when creating the move line from
        the move
        """
        res = super()._prepare_move_line_vals(
            quantity=quantity, reserved_quant=reserved_quant
        )
        if self.analytic_distribution:
            res.update({"analytic_distribution": self.analytic_distribution})
        return res


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line", "analytic.mixin"]

    @api.model
    def _prepare_stock_move_vals(self):
        """
        In the case move lines are created manually, we should fill in the
        new move created here with the analytic account if filled in.
        """
        res = super()._prepare_stock_move_vals()
        if self.analytic_distribution:
            res.update({"analytic_distribution": self.analytic_distribution})
        return res
