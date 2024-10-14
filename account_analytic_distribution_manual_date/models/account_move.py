# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        date = self._get_invoice_date(vals)

        invoice_line_ids = vals.get("invoice_line_ids", [])

        if invoice_line_ids:
            self._validate_manual_distributions(invoice_line_ids, date)
        elif "invoice_date" in vals:
            self._validate_existing_manual_distributions(date)

        return super().write(vals)

    def _get_invoice_date(self, vals):
        date_string = (
            vals.get("invoice_date")
            or self.invoice_date
            or vals.get("date")
            or self.date
        )
        return (
            fields.Date.from_string(date_string)
            if date_string
            else fields.Date.context_today(self)
        )

    def _validate_manual_distributions(self, invoice_line_ids, date):
        for line in invoice_line_ids:
            if len(line) > 2 and "manual_distribution_id" in line[2]:
                manual_distribution = self.env[
                    "account.analytic.distribution.manual"
                ].browse(line[2]["manual_distribution_id"])
                self._check_manual_distribution_date(manual_distribution, date)

    def _validate_existing_manual_distributions(self, date):
        for line in self.invoice_line_ids:
            manual_distribution = line.manual_distribution_id
            if manual_distribution:
                self._check_manual_distribution_date(manual_distribution, date)

    def _check_manual_distribution_date(self, manual_distribution, date):
        if manual_distribution and not (
            manual_distribution.start_date <= date <= manual_distribution.end_date
        ):
            raise UserError(
                _(
                    "The invoice date %(invoice_date)s is outside the "
                    "manual distribution period %(start_date)s - "
                    "%(end_date)s."
                )
                % {
                    "invoice_date": date,
                    "start_date": manual_distribution.start_date,
                    "end_date": manual_distribution.end_date,
                }
            )
