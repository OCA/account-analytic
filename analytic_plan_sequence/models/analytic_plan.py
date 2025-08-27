# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticPlan(models.Model):
    _inherit = "account.analytic.plan"
    _order = "sequence, complete_name asc"

    sequence = fields.Integer(default=10)

    @api.model
    def get_relevant_plans(self, **kwargs):
        res = super().get_relevant_plans(**kwargs)
        if not res:
            return res
        plans = {p.id: p for p in self.browse([d["id"] for d in res])}
        for d in res:
            d["sequence"] = plans[d["id"]].sequence
        return res
