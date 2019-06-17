# Copyright 2019 brain-tec AG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)

        # Add analytic account in debit line
        if self.analytic_account_id and res:
            for num in range(0, 2):
                res[num][2].update({
                    'analytic_account_id': self.analytic_account_id.id,
                })
        return res
