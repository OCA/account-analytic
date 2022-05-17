# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    @api.model
    def _update_analytic_account_policy_never(self, vals_list):
        """
        If an analytic account is provided in values for creation, we
        check that the policy on account type is 'never'.
        In that case, drop the analytic account.
        """
        for vals in vals_list:
            if "analytic_account_id" in vals:
                account = self.env["account.account"].browse(vals["account_id"])
                if account.user_type_id.property_analytic_policy == "never":
                    vals.pop("analytic_account_id")

    @api.model_create_multi
    def create(self, vals_list):
        self._update_analytic_account_policy_never(vals_list)
        return super().create(vals_list)
