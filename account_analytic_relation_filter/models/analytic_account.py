# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    relation_line_ids = fields.One2many("analytic.account.relation.line", "account_id")

    def get_related_account_ids(self):
        """Return related analytic accounts for distribution filtering."""
        related_plans = self.relation_line_ids.mapped("plan_id")
        other_plans = self.env["account.analytic.plan"].search(
            [("id", "not in", related_plans.ids)]
        )
        related_accounts = self.relation_line_ids.mapped(
            "account_ids"
        ) | other_plans.mapped("account_ids")
        return related_accounts.ids
