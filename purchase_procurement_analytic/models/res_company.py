# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    purchase_analytic_grouping = fields.Selection(
        [("order", "Per Order"), ("line", "Per line")],
        default="order",
        required=True,
    )
