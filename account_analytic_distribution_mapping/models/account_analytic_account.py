# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    mapped_account_ids = fields.Many2many(
        "account.analytic.account",
        relation="account_analytic_account_mapping_rel",
        column1="source_account_id",
        column2="dest_account_id",
        check_company=True,
        domain="[('root_plan_id', '!=', root_plan_id)]",
    )

    @api.constrains("mapped_account_ids", "plan_id")
    def _check_mapped_accounts(self):
        for account in self:
            dest_accounts = account.mapped_account_ids
            if not dest_accounts:
                continue
            if account.root_plan_id in dest_accounts.root_plan_id:
                raise ValidationError(
                    _(
                        "%(acc)s cannot be mapped to an account of its own root "
                        "plan (%(plan)s).",
                        acc=account.display_name,
                        plan=account.root_plan_id.display_name,
                    )
                )
            if len(dest_accounts) != len(dest_accounts.root_plan_id):
                raise ValidationError(
                    _(
                        "%(acc)s maps several accounts to the same root plan. "
                        "Only one mapped account per plan is allowed.",
                        acc=account.display_name,
                    )
                )
