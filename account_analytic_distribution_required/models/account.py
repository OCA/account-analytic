# Copyright 2014 Acsone - Stéphane Bidoul <stephane.bidoul@acsone.eu>
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    property_analytic_policy = fields.Selection(
        selection_add=[
            ("always_plan", "Always (analytic distribution)"),
            ("always_plan_or_account", "Always (analytic account or distribution)"),
        ],
    )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_analytic_distribution_required_msg(self):
        self.ensure_one()
        analytic_distribution = self.analytic_tag_ids.filtered(
            "active_analytic_distribution"
        )
        if self.analytic_account_id and analytic_distribution:
            return _(
                "Analytic account and analytic distribution are mutually exclusive"
            )
        analytic_policy = self.account_id._get_analytic_policy()
        if analytic_policy == "always_plan" and not analytic_distribution:
            return _(
                "Analytic policy is set to "
                "'Always (analytic distribution)' with account "
                "'%s' but the analytic distribution is "
                "missing in the account move line with "
                "label '%s'."
            ) % (
                self.account_id.display_name,
                self.name or "",
            )
        if (
            analytic_policy == "always_plan_or_account"
            and not self.analytic_account_id
            and not analytic_distribution
        ):
            return _(
                "Analytic policy is set to "
                "'Always (analytic account or distribution)' "
                "with account '%s' but the analytic "
                "distribution and the analytic account are "
                "missing in the account move line "
                "with label '%s'."
            ) % (
                self.account_id.display_name,
                self.name or "",
            )
        elif analytic_policy == "never" and analytic_distribution:
            return _(
                "Analytic policy is set to 'Never' with account "
                "'%s' but the account move line with label "
                "'%s' has an analytic distribution"
            ) % (
                self.account_id.display_name,
                self.name or "",
            )

    @api.constrains(
        "analytic_account_id", "analytic_tag_ids", "account_id", "debit", "credit"
    )
    def _check_analytic_required(self):
        for rec in self.filtered(lambda r: r.debit or r.credit):
            message = rec._check_analytic_distribution_required_msg()
            if message:
                raise exceptions.ValidationError(message)
        super()._check_analytic_required()
