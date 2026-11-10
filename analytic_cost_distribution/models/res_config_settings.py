# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    indirect_costs_root_plan_ids = fields.Many2many(
        related="company_id.indirect_costs_root_plan_ids",
        readonly=False,
    )
    profit_centres_root_plan_ids = fields.Many2many(
        related="company_id.profit_centres_root_plan_ids",
        readonly=False,
    )
