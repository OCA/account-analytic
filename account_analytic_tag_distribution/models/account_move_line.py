# Copyright 2023 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("analytic_tag_ids")
    def _onchange_analytic_tag_ids(self):
        """If any tag has a distribution, we will disable the standard analytical
        distribution."""
        if any(self.analytic_tag_ids.mapped("active_analytic_distribution")):
            self.analytic_distribution = False

    def _prepare_analytic_lines(self):
        """If any tag has distribution, we will not call super() to avoid conflicts
        with standard flow."""
        self.ensure_one()
        tags_with_distribution = self.analytic_tag_ids.filtered(
            lambda x: x.active_analytic_distribution
        )
        if not tags_with_distribution:
            return super()._prepare_analytic_lines()
        analytic_line_vals = []
        for tag in tags_with_distribution:
            distribution_on_each_plan = {}
            for account_id, distribution in tag.analytic_distribution.items():
                line_values = self._prepare_analytic_distribution_line(
                    float(distribution), account_id, distribution_on_each_plan
                )
                line_values.update({"tag_ids": [(6, 0, tag.ids)]})
                if not self.currency_id.is_zero(line_values.get("amount")):
                    analytic_line_vals.append(line_values)
        return analytic_line_vals
