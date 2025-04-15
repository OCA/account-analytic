# Copyright 2024 Tecnativa - Carlos Lopez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


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

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default)
        if "name" not in default:
            for record, vals in zip(self, vals_list, strict=False):
                vals["name"] = self.env._("%s (Copy)", record.name)
        return vals_list
