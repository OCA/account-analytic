# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    manual_distribution_id = fields.Many2one("account.analytic.distribution.manual")
