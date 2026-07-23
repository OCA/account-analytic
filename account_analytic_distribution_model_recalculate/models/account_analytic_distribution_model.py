# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    start_date = fields.Date()
    end_date = fields.Date()
    recalculate = fields.Boolean(
        help=(
            "If checked, you can synchronize and recalculate journal items "
            "that were created by this model and still match its criteria."
        ),
        default=False,
    )

    @api.depends(
        "account_prefix",
        "partner_id",
        "partner_category_id",
        "product_id",
        "product_categ_id",
        "start_date",
        "end_date",
    )
    def _compute_display_name(self):
        for model in self:
            parts = [
                value
                for value in (
                    model.account_prefix,
                    model.partner_id.name,
                    model.partner_category_id.name,
                    model.product_id.display_name,
                    model.product_categ_id.name,
                )
                if value
            ]
            display_name = " | ".join(parts) or self.env._(
                "Analytic Distribution Model"
            )
            if model.start_date or model.end_date:
                start_date = fields.Date.to_string(model.start_date) or ""
                end_date = fields.Date.to_string(model.end_date) or ""
                display_name = f"{display_name} ({start_date} - {end_date})"
            model.display_name = display_name

    @api.constrains("start_date", "end_date")
    def _check_start_date_before_end_date(self):
        for record in self:
            if (
                record.start_date
                and record.end_date
                and record.start_date > record.end_date
            ):
                raise ValidationError(
                    self.env._("The start date cannot be later than the end date.")
                )

    @api.constrains(
        "start_date",
        "end_date",
        "partner_id",
        "account_prefix",
        "partner_category_id",
        "product_id",
        "product_categ_id",
        "company_id",
    )
    def _check_overlapping_dates(self):
        for record in self:
            if self.search_count(record._get_overlap_domain(), limit=1):
                raise ValidationError(
                    self.env._(
                        "Another analytic distribution model with the same "
                        "conditions has an overlapping date range."
                    )
                )

    def _get_applicable_fields(self):
        """
        Returns the list of fields that are used to determine if
        there are any overlapping models. This method can be overridden in
        other modules to add more fields to the list.
        """
        fields = [
            "partner_id",
            "account_prefix",
            "partner_category_id",
            "product_id",
            "product_categ_id",
            "company_id",
        ]
        # Adds compatibility with pos_analytic_by_config module if installed
        if self.env["ir.module.module"].search_count(
            [("name", "=", "pos_analytic_by_config"), ("state", "=", "installed")],
            limit=1,
        ):
            fields.append("pos_config_id")
        return fields

    def _get_overlap_domain(self):
        self.ensure_one()
        domain = Domain("id", "!=", self.id or 0)
        fields = self._get_applicable_fields()

        for field_name in fields:
            value = self[field_name]
            if self._fields[field_name].type == "many2one":
                value = value.id
            domain &= Domain(field_name, "=", value or False)

        if self.end_date:
            domain &= Domain.OR(
                [
                    Domain("start_date", "=", False),
                    Domain("start_date", "<=", self.end_date),
                ]
            )
        if self.start_date:
            domain &= Domain.OR(
                [
                    Domain("end_date", "=", False),
                    Domain("end_date", ">=", self.start_date),
                ]
            )
        return domain

    def _create_domain(self, fname, value):
        if fname == "date":
            if not value:
                return []
            value = fields.Date.to_date(value)
            return [
                "&",
                "|",
                ("start_date", "<=", value),
                ("start_date", "=", False),
                "|",
                ("end_date", ">=", value),
                ("end_date", "=", False),
            ]
        return super()._create_domain(fname, value)

    @api.model
    def _get_distribution_and_models(self, vals):
        """Return the standard combined distribution and the models really used."""
        applicable_models = self._get_applicable_models(
            {
                key: value
                for key, value in vals.items()
                if key != "related_root_plan_ids"
            }
        )
        distribution = {}
        applied_models = self.browse()
        applied_plans = vals.get(
            "related_root_plan_ids", self.env["account.analytic.plan"]
        )

        for model in applicable_models:
            current_plans = model.distribution_analytic_account_ids.root_plan_id
            if current_plans and not applied_plans & current_plans:
                applied_plans += current_plans
                applied_models += model
                distribution = self._merge_distribution(
                    distribution,
                    model.analytic_distribution
                    | {
                        "__update__": current_plans.mapped(
                            lambda plan: plan._column_name()
                        )
                    },
                )
        return distribution, applied_models

    def _get_lines_domain(self):
        self.ensure_one()
        if not self.recalculate:
            raise ValidationError(
                self.env._("Enable recalculation before synchronizing journal items.")
            )
        if not self.account_prefix or not self.partner_id:
            raise ValidationError(
                self.env._(
                    "You must select a partner and account prefix to recalculate lines."
                )
            )

        domain = Domain.OR(
            [
                Domain(
                    "account_id.code",
                    "=ilike",
                    f"{account_code.strip()}%",
                )
                for account_code in self.account_prefix.split(",")
                if account_code.strip()
            ]
        )
        domain &= Domain("partner_id", "=", self.partner_id.id)
        if self.start_date:
            domain &= Domain("date", ">=", self.start_date)
        if self.end_date:
            domain &= Domain("date", "<=", self.end_date)
        if self.partner_category_id:
            domain &= Domain(
                "partner_id.category_id", "in", self.partner_category_id.ids
            )
        if self.product_categ_id:
            domain &= Domain("product_id.categ_id", "=", self.product_categ_id.id)
        if self.product_id:
            domain &= Domain("product_id", "=", self.product_id.id)
        if self.company_id:
            domain &= Domain("company_id", "=", self.company_id.id)
        return domain

    def _notification_action(self, updated_lines, title):
        message = (
            self.env._("%s journal items have been updated.", updated_lines)
            if updated_lines
            else self.env._("No journal items have been updated.")
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }

    def action_recalculate_analytic_lines(self):
        updated_lines = 0
        for record in self:
            lines = self.env["account.move.line"].search(
                record._get_lines_domain()
                & Domain("distribution_model_ids", "in", record.ids)
            )
            updated_lines += lines._recompute_distribution_models()
        return self._notification_action(
            updated_lines, self.env._("Recalculation Complete")
        )

    def action_sync_lines(self):
        updated_lines = 0
        for record in self:
            current_lines = self.env["account.move.line"].search(
                [("distribution_model_ids", "in", record.ids)]
            )
            candidate_lines = self.env["account.move.line"].search(
                record._get_lines_domain()
            )
            updated_lines += (
                current_lines | candidate_lines
            )._sync_distribution_models()
        return self._notification_action(
            updated_lines, self.env._("Synchronization Complete")
        )
