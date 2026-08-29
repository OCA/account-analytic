# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    analytic_distribution = fields.Json(
        related="company_id.analytic_distribution", readonly=False
    )
    analytic_precision = fields.Integer(related="company_id.analytic_precision")
    distribution_analytic_account_ids = fields.Many2many(
        related="company_id.distribution_analytic_account_ids", readonly=False
    )
