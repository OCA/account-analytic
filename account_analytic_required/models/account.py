# Copyright 2011-2020 Akretion - Alexis de Lattre
# Copyright 2016-2020 Camptocamp SA
# Copyright 2020 Druidoo - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, exceptions, fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    property_analytic_policy = fields.Selection(
        selection=[
            ("optional", "Optional"),
            ("always", "Always"),
            ("posted", "Posted moves"),
            ("never", "Never"),
        ],
        string="Policy for analytic account",
        default="optional",
        company_dependent=True,
        help=(
            "Sets the policy for analytic accounts.\n"
            "If you select:\n"
            "- Optional: The accountant is free to put an analytic account "
            "on an account move line with this type of account.\n"
            "- Always: The accountant will get an error message if "
            "there is no analytic account.\n"
            "- Posted moves: The accountant will get an error message if no "
            "analytic account is defined when the move is posted.\n"
            "- Never: The accountant will get an error message if an analytic "
            "account is present.\n\n"
            "This field is company dependent."
        ),
    )


class AccountAccount(models.Model):
    _inherit = "account.account"

    def _get_analytic_policy(self):
        """Extension point to obtain analytic policy for an account"""
        self.ensure_one()
        return self.user_type_id.with_company(
            self.company_id.id
        ).property_analytic_policy


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        self.mapped("line_ids")._check_analytic_required()
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _has_analytic_distribution(self):
        # If the move line has an analytic tag with distribution, the field
        # analytic_account_id may be empty. So in this case, we do not check it.
        tags_with_analytic_distribution = self.analytic_tag_ids.filtered(
            "active_analytic_distribution"
        )
        return bool(tags_with_analytic_distribution.analytic_distribution_ids)

    def _check_analytic_required_msg(self):
        self.ensure_one()
        company_cur = self.company_currency_id
        if company_cur.is_zero(self.debit) and company_cur.is_zero(self.credit):
            return None
        analytic_policy = self.account_id._get_analytic_policy()
        if (
            analytic_policy == "always"
            and not self.analytic_account_id
            and not self._has_analytic_distribution()
        ):
            return _(
                "Analytic policy is set to 'Always' with account "
                "'%s' but the analytic account is missing in "
                "the account move line with label '%s'."
            ) % (
                self.account_id.display_name,
                self.name or "",
            )
        elif analytic_policy == "never" and (
            self.analytic_account_id or self._has_analytic_distribution()
        ):
            analytic_account = (
                self.analytic_account_id
                or self.analytic_tag_ids.analytic_distribution_ids[:1]
            )
            return _(
                "Analytic policy is set to 'Never' with account "
                "'%s' but the account move line with label '%s' "
                "has an analytic account '%s'."
            ) % (
                self.account_id.display_name,
                self.name or "",
                analytic_account.display_name,
            )
        elif (
            analytic_policy == "posted"
            and not self.analytic_account_id
            and self.move_id.state == "posted"
            and not self._has_analytic_distribution()
        ):
            return _(
                "Analytic policy is set to 'Posted moves' with "
                "account '%s' but the analytic account is missing "
                "in the account move line with label '%s'."
            ) % (
                self.account_id.display_name,
                self.name or "",
            )
        return None

    @api.constrains("analytic_account_id", "account_id", "debit", "credit")
    def _check_analytic_required(self):
        for rec in self:
            message = rec._check_analytic_required_msg()
            if message:
                raise exceptions.ValidationError(message)
