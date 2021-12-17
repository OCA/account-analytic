# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
    )
    account_analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
    )
