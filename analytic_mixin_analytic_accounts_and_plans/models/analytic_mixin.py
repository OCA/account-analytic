# Copyright 2023 Quartile Limited (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from collections import defaultdict

from odoo import api, fields, models


class AnalyticMixin(models.AbstractModel):
    _inherit = "analytic.mixin"

    analytic_account_ids = fields.Many2many(
        "account.analytic.account",
        compute="_compute_analytic_accounts_and_plans",
        string="Analytic Accounts",
        help="Analytic accounts computed from analytic distribution.",
    )
    analytic_account_names = fields.Char(
        compute="_compute_analytic_accounts_and_plans",
        help="Comma-separated analytic account names, in case it is useful to be "
        "included in the exported data.",
    )
    analytic_plan_ids = fields.Many2many(
        "account.analytic.plan",
        compute="_compute_analytic_accounts_and_plans",
        string="Analytic Plans",
        help="Analytic plans computed from analytic distribution.",
    )
    analytic_plan_names = fields.Char(
        compute="_compute_analytic_accounts_and_plans",
        help="Comma-separated analytic plan names, in case it is useful to be "
        "included in the exported data.",
    )

    def _compute_analytic_accounts_and_plans(self):
        if self._fields["analytic_account_ids"].store:
            # assume all 4 fields are stored
            return self._compute_stored_analytic_accounts_and_plans()
        else:
            return self._compute_unstored_analytic_accounts_and_plans()

    # TODO: Compare the performance of the two methods. Do we need both?

    def _compute_unstored_analytic_accounts_and_plans(self):
        Analytic_account = self.env["account.analytic.account"]
        Analytic_plan = self.env["account.analytic.plan"]
        for rec in self:
            if not rec.analytic_distribution:
                rec.analytic_account_ids = Analytic_account
                rec.analytic_account_names = False
                rec.analytic_plan_ids = Analytic_plan
                rec.analytic_plan_names = False
                continue
            account_ids = [int(key) for key in rec.analytic_distribution.keys()]
            rec.analytic_account_ids = Analytic_account.browse(account_ids)
            rec.analytic_account_names = ", ".join(
                account.display_name for account in rec.analytic_account_ids
            )
            rec.analytic_plan_ids = rec.analytic_account_ids.plan_id
            rec.analytic_plan_names = ", ".join(
                plan.display_name for plan in rec.analytic_plan_ids
            )

    # AGPL (copied from account_financial_report)
    @api.depends("analytic_distribution")
    def _compute_stored_analytic_accounts_and_plans(self):
        # Prefetch all involved analytic accounts
        with_distribution = self.filtered("analytic_distribution")
        batch_by_analytic_account = defaultdict(list)
        for record in with_distribution:
            for account_id in map(int, record.analytic_distribution):
                batch_by_analytic_account[account_id].append(record.id)
        existing_account_ids = set(
            self.env["account.analytic.account"]
            .browse(map(int, batch_by_analytic_account))
            .exists()
            .ids
        )
        # Store them
        self.analytic_account_ids = False
        for account_id, record_ids in batch_by_analytic_account.items():
            if account_id not in existing_account_ids:
                continue
            self.browse(record_ids).analytic_account_ids = [
                fields.Command.link(account_id)
            ]
            plan_id = self.env["account.analytic.account"].browse(account_id).plan_id.id
            self.browse(record_ids).analytic_plan_ids = [fields.Command.link(plan_id)]
