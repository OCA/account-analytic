# Copyright 2023 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from collections import defaultdict

from odoo import Command, api, fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        compute="_compute_analytic_account_ids",
        string="Analytic Accounts",
        help="Analytic accounts computed from analytic distribution.",
    )
    analytic_account_names = fields.Char(
        compute="_compute_analytic_account_names",
        help="Comma-separated analytic account names, in case it is useful to be "
        "included in the exported data.",
    )

    @api.depends("analytic_distribution")
    def _compute_analytic_account_ids(self):
        # Prefetch all involved analytic accounts
        with_distribution = self.filtered("analytic_distribution")
        batch_by_analytic_account = defaultdict(list)
        for record in with_distribution:
            for account_id in map(int, record.analytic_distribution):
                batch_by_analytic_account[account_id].append(record.id)
        existing_account_ids = set(
            self.env["account.analytic.account"]
            .browse(map(int, batch_by_analytic_account))
            .exists()  # Else the `Command.link()` may raise
            .ids
        )
        # Store them. Grouping by `record_ids` allows better performance.
        self.analytic_account_ids = False
        for account_id, record_ids in batch_by_analytic_account.items():
            if account_id not in existing_account_ids:
                continue
            self.browse(record_ids).analytic_account_ids = [Command.link(account_id)]

    @api.depends("analytic_account_ids")
    def _compute_analytic_account_names(self):
        for rec in self:
            rec.analytic_account_names = ", ".join(
                account.display_name for account in rec.analytic_account_ids
            )
