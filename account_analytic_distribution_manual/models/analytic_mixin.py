# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    # it will not be a many2one field
    manual_distribution_id = fields.Integer(string="Manual Distribution ID")
