from odoo import api, fields, models


class AccountAnalyticDistribution(models.Model):
    _inherit = "account.analytic.distribution.model"

    affected_accounts = fields.Many2many(
        comodel_name="account.account",
        help="Accounts that are affected by this distribution model.",
        compute="_compute_affected_accounts",
    )

    @api.depends("account_prefix")
    def _compute_affected_accounts(self):
        for distribution in self:
            if distribution.account_prefix:
                distribution.affected_accounts = (
                    self.env["account.account"]
                    .search([("code", "=ilike", f"{distribution.account_prefix}%")])
                    .ids
                )
            else:
                distribution.affected_accounts = [(5, 0, 0)]
