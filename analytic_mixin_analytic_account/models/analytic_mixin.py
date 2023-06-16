# Copyright 2023 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import Command, api, fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        compute="_compute_analytic_account_ids",
        context={"active_test": False},
        string="Analytic Accounts",
        help="Analytic accounts computed from analytic distribution.",
    )
    analytic_account_names = fields.Char(
        compute="_compute_analytic_account_ids",
        help="Comma-separated analytic account names, in case it is useful to be "
        "included in the exported data.",
    )

    @api.depends("analytic_distribution")
    def _compute_analytic_account_ids(self):
        for rec in self:
            if not rec.analytic_distribution:
                rec.analytic_account_ids = False
                rec.analytic_account_names = False
                continue
            account_ids = [int(key) for key in rec.analytic_distribution.keys()]
            rec.analytic_account_ids = [Command.set(account_ids)]
            rec.analytic_account_names = ", ".join(
                account.display_name for account in rec.analytic_account_ids
            )
