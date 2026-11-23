# Copyright 2024 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Import helper columns: not stored, they only carry values during
    # import and are translated into analytic_distribution on the fly.
    analytic_1_id = fields.Many2one("account.analytic.account", store=False)
    analytic_2_id = fields.Many2one("account.analytic.account", store=False)
    analytic_3_id = fields.Many2one("account.analytic.account", store=False)
    analytic_4_id = fields.Many2one("account.analytic.account", store=False)

    _analytic_import_columns = (
        "analytic_1_id",
        "analytic_2_id",
        "analytic_3_id",
        "analytic_4_id",
    )

    @api.model
    def _get_import_analytic_distribution(self, values):
        account_ids = []
        for column in self._analytic_import_columns:
            value = values.get(column)
            if isinstance(value, models.BaseModel):
                value = value.id
            if value:
                account_ids.append(value)
        if account_ids:
            return {
                ",".join(str(account_id) for account_id in account_ids): 100,
            }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("analytic_distribution"):
                distribution = self._get_import_analytic_distribution(vals)
                if distribution:
                    vals["analytic_distribution"] = distribution
        return super().create(vals_list)

    def write(self, vals):
        if any(column in vals for column in self._analytic_import_columns):
            if not vals.get("analytic_distribution"):
                distribution = self._get_import_analytic_distribution(vals)
                if distribution:
                    vals["analytic_distribution"] = distribution
        return super().write(vals)
