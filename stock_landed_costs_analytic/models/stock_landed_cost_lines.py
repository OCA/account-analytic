# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLandedCostLines(models.Model):

    _name = "stock.landed.cost.lines"
    _inherit = ["stock.landed.cost.lines", "analytic.mixin"]

    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
