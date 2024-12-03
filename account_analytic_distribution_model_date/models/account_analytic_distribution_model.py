# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticDistributionModel(models.Model):
    _inherit = ["account.analytic.distribution.model"]

    start_date = fields.Date()
    end_date = fields.Date()

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

    def _check_score(self, key, value):
        self.ensure_one()
        if key == "start_date" or key == "end_date":
            return 1

        return super()._check_score(key, value)

    @api.onchange("start_date", "end_date", "partner_id", "account_prefix")
    def _check_duplicate_dates(self):
        """
        Check if there are more than 1 register with overlapping dates
        for the same partner and prefix.
        """
        start_date = self.start_date if self.start_date else False
        end_date = self.end_date if self.end_date else False
        partner_id = self.partner_id.id if self.partner_id.id else False
        account_prefix = self.account_prefix[0] if self.account_prefix else False

        domain = [
            ("partner_id", "=", partner_id),
            ("company_id", "=", self.company_id.id),
        ]

        if self.ids:
            domain.append(("id", "!=", self.ids[0]))

        if account_prefix:
            domain.append(("account_prefix", "=ilike", f"{account_prefix}%"))
        else:
            domain.append(("account_prefix", "=", False))

        domain_without_dates = domain + [
            ("start_date", "=", False),
            ("end_date", "=", False),
        ]
        duplicate_without_dates = self.search(domain_without_dates)

        if start_date and not end_date:
            domain.append(("end_date", ">=", start_date))
        elif start_date and end_date:
            domain.append("|")
            domain.append(("start_date", "<=", end_date))
            domain.append(("start_date", "=", False))

        if end_date and not start_date:
            domain.append(("start_date", "<=", end_date))
        elif end_date and start_date:
            domain.append("|")
            domain.append(("end_date", ">=", start_date))
            domain.append(("end_date", "=", False))

        duplicate = self.search(domain)

        if duplicate or duplicate_without_dates:
            raise ValidationError(
                _(
                    "Cannot have overlapping dates for "
                    + "the same partner and account prefix."
                )
            )
