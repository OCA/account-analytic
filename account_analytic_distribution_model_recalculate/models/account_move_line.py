# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import Command
from odoo.tools import frozendict


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    distribution_model_ids = fields.Many2many(
        comodel_name="account.analytic.distribution.model",
        relation="account_move_line_analytic_distribution_model_rel",
        column1="move_line_id",
        column2="distribution_model_id",
        string="Distribution Models",
        copy=False,
        readonly=True,
    )

    @api.depends("account_id", "partner_id", "product_id", "date", "invoice_date")
    def _compute_analytic_distribution(self):
        cache = {}
        for line in self:
            if line.display_type == "product" or not line.move_id.is_invoice(
                include_receipts=True
            ):
                related_distribution = line._related_analytic_distribution()
                root_plans = (
                    self.env["account.analytic.account"]
                    .browse(
                        list(
                            {
                                int(account_id)
                                for account_ids in related_distribution
                                for account_id in account_ids.split(",")
                                if account_id.strip()
                            }
                        )
                    )
                    .exists()
                    .root_plan_id
                )
                arguments = frozendict(
                    line._get_analytic_distribution_arguments(root_plans)
                )
                if arguments not in cache:
                    cache[arguments] = self.env[
                        "account.analytic.distribution.model"
                    ]._get_distribution_and_models(arguments)
                model_distribution, distribution_models = cache[arguments]
                line.analytic_distribution = (
                    related_distribution | model_distribution
                    or line.analytic_distribution
                )
                line.distribution_model_ids = distribution_models

    def _get_analytic_distribution_arguments(self, root_plans):
        arguments = super()._get_analytic_distribution_arguments(root_plans)
        arguments["date"] = (
            self.invoice_date or self.date or fields.Date.context_today(self)
        )
        return arguments

    def _get_distribution_models_data(self):
        self.ensure_one()
        if not (
            self.display_type == "product"
            or not self.move_id.is_invoice(include_receipts=True)
        ):
            return self.analytic_distribution or {}, self.env[
                "account.analytic.distribution.model"
            ]

        related_distribution = self._related_analytic_distribution()
        root_plans = (
            self.env["account.analytic.account"]
            .browse(
                list(
                    {
                        int(account_id)
                        for account_ids in related_distribution
                        for account_id in account_ids.split(",")
                        if account_id.strip()
                    }
                )
            )
            .exists()
            .root_plan_id
        )
        arguments = self._get_analytic_distribution_arguments(root_plans)
        model_distribution, models_applied = self.env[
            "account.analytic.distribution.model"
        ]._get_distribution_and_models(arguments)
        return related_distribution | model_distribution, models_applied

    def _sync_distribution_models(self):
        updated = 0
        for line in self:
            _distribution, models_applied = line._get_distribution_models_data()
            if line.distribution_model_ids != models_applied:
                line.distribution_model_ids = models_applied
                updated += 1
        return updated

    def _recompute_distribution_models(self):
        updated = 0
        for line in self:
            distribution, models_applied = line._get_distribution_models_data()
            values = {}
            if line.analytic_distribution != distribution:
                values["analytic_distribution"] = distribution
            if line.distribution_model_ids != models_applied:
                values["distribution_model_ids"] = [Command.set(models_applied.ids)]
            if values:
                line.write(values)
                updated += 1
        return updated
