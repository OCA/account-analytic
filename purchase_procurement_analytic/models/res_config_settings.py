# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    purchase_analytic_grouping = fields.Selection(
        related="company_id.purchase_analytic_grouping",
        readonly=False,
        required=True,
    )
