# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super()._prepare_stock_move_vals(first_line, order_lines)
        account_analytic_id = first_line.order_id.config_id.account_analytic_id
        if account_analytic_id:
            res.update({"analytic_account_id": account_analytic_id.id})
        return res
