# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLandedCostLines(models.Model):

    _inherit = "stock.landed.cost.lines"

    analytic_account_id = fields.Many2one(
        string="Analytic Account", comodel_name="account.analytic.account",
    )
    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
