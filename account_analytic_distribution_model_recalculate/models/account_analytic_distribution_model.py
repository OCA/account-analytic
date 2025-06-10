# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.analytic.models.analytic_distribution_model import (
    NonMatchingDistribution,
)


class AccountAnalyticDistributionModel(models.Model):
    _inherit = ["account.analytic.distribution.model"]

    start_date = fields.Date()
    end_date = fields.Date()
    recalculate = fields.Boolean(
        help="""If checked, you will be able to recalculate
        the analytic lines that where  created by this model,
        and still matches the model criteria""",
        default=False,
    )

    def _compute_display_name(self):
        for model in self:
            parts = []

            if model.account_prefix:
                parts.append(model.account_prefix)

            if model.partner_id:
                parts.append(model.partner_id.name)

            if model.partner_category_id:
                parts.append(model.partner_category_id.name)

            if model.product_id:
                parts.append(model.product_id.display_name)

            if model.product_categ_id:
                parts.append(model.product_categ_id.name)

            main_info = " | ".join(parts)

            start_date = (
                model.start_date.strftime("%Y-%m-%d") if model.start_date else ""
            )
            end_date = model.end_date.strftime("%Y-%m-%d") if model.end_date else ""

            date_info = f"{start_date} - {end_date}" if start_date or end_date else ""

            model.display_name = f"{main_info} ({date_info})"

    @api.constrains("start_date", "end_date")
    def _check_start_date_before_end_date(self):
        for record in self:
            if (
                record.start_date
                and record.end_date
                and record.start_date > record.end_date
            ):
                raise ValidationError(
                    _("The start date cannot be later than the end date.")
                )

    @api.onchange(
        "start_date",
        "end_date",
        "partner_id",
        "account_prefix",
        "partner_category_id",
        "product_id",
        "product_categ_id",
    )
    def _check_duplicate_dates(self):
        """
        Check if there are more than 1 register with overlapping dates
        """

        for record in self:
            domain = record._get_domain()

            if record.ids:
                domain.append(("id", "!=", record.ids[0]))

            domain_without_dates = domain + [
                ("start_date", "=", False),
                ("end_date", "=", False),
            ]
            duplicate_without_dates = self.search(domain_without_dates)

            duplicate = self.search(domain)

            if duplicate or duplicate_without_dates:
                raise ValidationError(
                    _(
                        "Cannot have overlapping dates for "
                        + "the same partner and account prefix."
                    )
                )

    @api.model
    def _get_distribution(self, vals):
        """
        Override the _get_distribution method to add the distribution_model_id
        to the result.
        """
        if self.env.context.get("get_distributiion_model_id"):
            domain = []
            for fname, value in vals.items():
                domain += self._create_domain(fname, value) or []
            best_score = 0
            res = {}
            fnames = set(self._get_fields_to_check())
            for rec in self.search(domain):
                try:
                    score = sum(rec._check_score(key, vals.get(key)) for key in fnames)
                    if score > best_score:
                        res = rec
                        best_score = score
                except NonMatchingDistribution:
                    continue
            return res
        else:
            return super()._get_distribution(vals)

    def _get_fields_to_check(self):
        # Exclude the recalculate field from the fields to check
        # to avoid NonMatchingDistribution
        return [f for f in super()._get_fields_to_check() if f != "recalculate"]

    def _check_score(self, key, value):
        self.ensure_one()
        if key == "start_date" or key == "end_date":
            return 1

        return super()._check_score(key, value)

    def _create_domain(self, fname, value):
        if fname == "date" and value:
            return [
                "|",
                "&",
                ("start_date", "<=", value),
                ("end_date", ">=", value),
                "|",
                "&",
                ("start_date", "<=", value),
                ("end_date", "=", False),
                "|",
                "&",
                ("start_date", "=", False),
                ("end_date", ">=", value),
                "&",
                ("start_date", "=", False),
                ("end_date", "=", False),
            ]
        return super()._create_domain(fname, value)

    def _get_domain(self):
        self.ensure_one()

        def safe(field, operator, value):
            return (field, operator, value) if value else None

        domain = list(
            filter(
                None,
                [
                    safe("partner_id", "=", self.partner_id.id),
                    safe("company_id", "=", self.company_id.id),
                    safe("product_id", "=", self.product_id.id),
                    safe("product_categ_id", "=", self.product_categ_id.id),
                    safe("partner_category_id", "=", self.partner_category_id.id),
                    (
                        safe("account_prefix", "=ilike", f"{self.account_prefix}%")
                        if self.account_prefix
                        else ("account_prefix", "=", False)
                    ),
                ],
            )
        )

        if self.start_date and self.end_date:
            domain += [
                "&",
                ("start_date", "<=", self.end_date),
                ("end_date", ">=", self.start_date),
            ]
        elif self.start_date:
            domain.append(("end_date", ">=", self.start_date))
        elif self.end_date:
            domain.append(("start_date", "<=", self.end_date))

        return domain

    def _get_message(self, updated_lines):
        return (
            _("%s analytic lines have been recalculated.") % updated_lines
            if updated_lines
            else _("No analytic lines have been recalculated.")
        )

    def _get_lines_domain(self):
        self.ensure_one()

        def _add_condition(domain, field, operator, value):
            if value:
                domain.append((field, operator, value.id))

        if not self.recalculate:
            pass

        if not self.account_prefix or not self.partner_id:
            # To avoid massive recalculation of all lines just
            # recalculate the lines that has the same partner and account prefix
            raise ValidationError(
                _(
                    "You must select a partner and account prefix "
                    "to recalculate lines."
                )
            )

        domain = []

        start_date = self.start_date
        end_date = self.end_date

        if start_date and end_date:
            domain += [
                "&",
                ("date", "<=", end_date),
                ("date", ">=", start_date),
            ]
        elif start_date:
            domain.append(("date", ">=", start_date))
        elif end_date:
            domain.append(("date", "<=", end_date))

        if self.account_prefix:
            domain.append(("account_id.code", "=ilike", f"{self.account_prefix}%"))

        _add_condition(domain, "partner_id", "=", self.partner_id)
        _add_condition(domain, "partner_id.category_id", "=", self.partner_category_id)
        _add_condition(domain, "product_id.categ_id", "=", self.product_categ_id)
        _add_condition(domain, "product_id", "=", self.product_id)

        return domain

    def action_recalculate_analytic_lines(self):
        """
        Recalculate the analytic lines that match the distribution model
        and where generated by himself.
        """

        for record in self:
            domain = record._get_lines_domain()
            domain.append(("distribution_model_id", "=", record.id))

            domain.append(("analytic_distribution", "!=", record.analytic_distribution))

            lines_to_update = self.env["account.move.line"].search(domain)

            if lines_to_update:
                lines_to_update.write(
                    {"analytic_distribution": record.analytic_distribution}
                )

            message = self._get_message(len(lines_to_update))

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Recalculation Complete"),
                "message": message,
                "type": "success",
                "sticky": False,
            },
        }

    def action_sync_lines(self):
        """
        Sync the jorurnal items that match the distribution model
        """

        for record in self:
            actual_lines = self.env["account.move.line"].search(
                [
                    ("distribution_model_id", "=", record.id),
                ]
            )
            actual_lines.write({"distribution_model_id": False})

            domain = record._get_lines_domain()
            lines = self.env["account.move.line"].search(domain)

            lines.write(
                {
                    "distribution_model_id": record.id,
                }
            )
