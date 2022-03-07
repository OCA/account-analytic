# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        help="Choose an analytic account that will be used as default on new pickings",
    )
