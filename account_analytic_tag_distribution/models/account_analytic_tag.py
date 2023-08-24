# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class AccountAnalyticTag(models.Model):
    _name = "account.analytic.tag"
    _inherit = ["account.analytic.tag", "analytic.mixin"]

    active_analytic_distribution = fields.Boolean(string="Analytic Distribution")

    @api.onchange("active_analytic_distribution")
    def _onchange_active_analytic_distribution(self):
        if self.active_analytic_distribution:
            self.account_analytic_id = False

    def write(self, values):
        if values.get("active_analytic_distribution"):
            values["account_analytic_id"] = False
        return super().write(values)
