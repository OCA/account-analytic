# Copyright 2026 Akretion - Raphael Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    def _inject_parent_analytics(self, vals):
        """
        Intercepts analytic_distribution before save.
        If a child account is present, it automatically injects
        the parent account into the JSON for hierarchical reporting.
        """
        if not vals.get("analytic_distribution"):
            return

        dist = vals["analytic_distribution"]

        # Safety check: Sometimes it comes as a string during imports
        if isinstance(dist, str):
            try:
                dist = json.loads(dist)
            except Exception:
                return

        if isinstance(dist, dict):
            new_dist = dict(dist)
            account_model = self.env["account.analytic.account"]

            # Get all account IDs currently in the JSON
            # Keys might be strings, and we ignore 'False'
            account_ids = [
                int(k)
                for k in dist.keys()
                if k != "False" and str(k).lstrip("-").isdigit()
            ]

            if not account_ids:
                return

            accounts = account_model.browse(account_ids)

            for acc in accounts:
                if acc.parent_id and str(acc.parent_id.id) not in new_dist:
                    # Copy the exact same percentage from child to parent
                    new_dist[str(acc.parent_id.id)] = dist[str(acc.id)]

            vals["analytic_distribution"] = new_dist

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._inject_parent_analytics(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._inject_parent_analytics(vals)
        return super().write(vals)
