# Copyright 2024 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_1_id = fields.Many2one("account.analytic.account")
    analytic_2_id = fields.Many2one("account.analytic.account")
    analytic_3_id = fields.Many2one("account.analytic.account")
    analytic_4_id = fields.Many2one("account.analytic.account")

    def _get_analytic_distribution(self, row):
        COLS = ["analytic_1_id", "analytic_2_id", "analytic_3_id", "analytic_4_id"]
        analytic_ids = [row.get(col) for col in COLS if row.get(col)]
        if analytic_ids:
            return {",".join([str(x) for x in analytic_ids]): 100}

    @api.model_create_multi
    def create(self, vals_list):
        for row in vals_list:
            if not row.get("analytic_distribution"):
                distribution = self._get_analytic_distribution(row)
                row["analytic_distribution"] = distribution
        return super().create(vals_list)
