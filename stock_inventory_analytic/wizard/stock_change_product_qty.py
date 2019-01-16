# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Analytic Account')

    def _action_start_line(self):
        res = super(StockChangeProductQty, self)._action_start_line()
        if self.analytic_account_id:
            res.update({'analytic_account_id': self.analytic_account_id.id})
        return res
