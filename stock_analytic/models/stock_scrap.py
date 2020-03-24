# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    analytic_account_id = fields.Many2one(
        string="Analytic Account", comodel_name="account.analytic.account"
    )

    def _prepare_move_values(self):
        res = super()._prepare_move_values()
        res.update({"analytic_account_id": self.analytic_account_id.id})
        return res
