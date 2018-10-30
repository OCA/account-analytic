# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2018 Hibou Corp.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        comodel_name='account.analytic.account',
    )

    @api.multi
    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id)
        # Add analytic account in debit line
        if not self.analytic_account_id:
            return res

        for num in range(0, 2):
            if res[num][2]["account_id"] != self.product_id.\
                    categ_id.property_stock_valuation_account_id.id:
                res[num][2].update({
                    'analytic_account_id': self.analytic_account_id.id,
                })
        return res
