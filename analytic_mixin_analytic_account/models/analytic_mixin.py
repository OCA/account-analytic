# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        compute="_compute_analytic_account_ids",
        string="Analytic Accounts",
        help="Analytic accounts computed from analytic distribution.",
    )
    analytic_account_names = fields.Char(
        compute="_compute_analytic_account_ids",
        help="Comma-separated analytic account names, in case it is useful to be "
        "included in the exported data.",
    )

    def _compute_analytic_account_ids(self):
        analytic_account = self.env["account.analytic.account"]
        for rec in self:
            if not rec.analytic_distribution:
                rec.analytic_account_ids = analytic_account
                rec.analytic_account_names = False
                continue
            account_ids = [int(key) for key in rec.analytic_distribution.keys()]
            rec.analytic_account_ids = analytic_account.browse(account_ids)
            rec.analytic_account_names = ", ".join(
                account.display_name for account in rec.analytic_account_ids
            )
