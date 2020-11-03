# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    analytic_account_id = fields.Many2one(
        related="company_id.analytic_account_id", readonly=False
    )
    analytic_tag_ids = fields.Many2many(
        related="company_id.analytic_tag_ids", readonly=False
    )
