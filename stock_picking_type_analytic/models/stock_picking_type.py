# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _name = "stock.picking.type"
    _inherit = ["stock.picking.type", "analytic.mixin"]

    analytic_distribution = fields.Json(
        help="Choose an analytic distribution to use as default on new pickings",
    )
