# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mrp_analytic_on_finished = fields.Boolean(
        related="company_id.mrp_analytic_on_finished",
        readonly=False,
    )
