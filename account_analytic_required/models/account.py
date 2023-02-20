# Copyright 2011-2020 Akretion - Alexis de Lattre
# Copyright 2016-2020 Camptocamp SA
# Copyright 2020 Druidoo - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, exceptions, fields, models


class AccountAccount(models.Model):
    _inherit = "account.account"

    analytic_policy = fields.Selection(
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

    def _get_analytic_policy(self):
        """Extension point to obtain analytic policy for an account"""
        self.ensure_one()
        return self.analytic_policy


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        self.mapped("line_ids")._check_analytic_required()
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _check_analytic_required_msg(self):
        self.ensure_one()
        company_cur = self.company_currency_id
        if company_cur.is_zero(self.debit) and company_cur.is_zero(self.credit):
            return None
        analytic_policy = self.account_id._get_analytic_policy()
        if analytic_policy == "always" and not self.analytic_distribution:
            return _(
                "Analytic policy is set to 'Always' with account "
                "'%(account)s' but the analytic account is missing in "
                "the account move line with label '%(move)s'."
            ) % {
                "account": self.account_id.display_name,
                "move": self.name or "",
            }
        elif analytic_policy == "never" and (self.analytic_distribution):
            analytic_account = self.analytic_distribution
            analytic_acc_ids = [int(k) for k in analytic_account.keys()]
            analytic_accs = self.env["account.analytic.account"].browse(
                analytic_acc_ids
            )
            return _(
                "Analytic policy is set to 'Never' with account "
                "'%(account)s' but the account move line with label '%(move)s' "
                "has an analytic account '%(analytic_account)s'."
            ) % {
                "account": self.account_id.display_name,
                "move": self.name or "",
                "analytic_account": ", ".join(analytic_accs.mapped("name")),
            }
        elif (
            analytic_policy == "posted"
            and not self.analytic_distribution
            and self.move_id.state == "posted"
        ):
            return _(
                "Analytic policy is set to 'Posted moves' with "
                "account '%(account)s' but the analytic account is missing "
                "in the account move line with label '%(move)s'."
            ) % {
                "account": self.account_id.display_name,
                "move": self.name or "",
            }
        return None

    @api.constrains("analytic_distribution", "account_id", "debit", "credit")
    def _check_analytic_required(self):
        for rec in self:
            message = rec._check_analytic_required_msg()
            if message:
                raise exceptions.ValidationError(message)
