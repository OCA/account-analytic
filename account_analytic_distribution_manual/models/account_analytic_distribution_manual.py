# Copyright 2024 Tecnativa - Carlos Lopez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class AccountAnalyticDistributionManual(models.Model):
    _name = "account.analytic.distribution.manual"
    _inherit = "analytic.mixin"
    _description = "Account analytic distribution manual"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )

    _sql_constraints = [
        (
            "unique_name_by_company",
            "unique(name, company_id)",
            "The name must be unique per Company!",
        ),
    ]

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        if "name" not in default:
            default["name"] = _("%s (Copy)") % self.name
        return super().copy(default=default)
