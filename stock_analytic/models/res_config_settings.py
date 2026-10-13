# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_analytic_on_valuation = fields.Boolean(
        related="company_id.stock_analytic_on_valuation",
        readonly=False,
    )
