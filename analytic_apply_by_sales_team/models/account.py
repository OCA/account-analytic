from odoo import models, fields, api
from odoo.tools import frozendict


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    team_id = fields.Many2one("crm.team", string="Sale Team")

    def _get_default_search_domain_vals(self):
        return super()._get_default_search_domain_vals() | {
            "team_id": False,
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("account_id", "partner_id", "product_id", "move_id.team_id")
    def _compute_analytic_distribution(self):
        cache = {}
        for line in self:
            if line.display_type == "product" or not line.move_id.is_invoice(
                include_receipts=True
            ):
                related_distribution = line._related_analytic_distribution()
                root_plans = (
                    self.env["account.analytic.account"]
                    .browse(
                        list(
                            {
                                int(account_id)
                                for ids in related_distribution
                                for account_id in ids.split(",")
                                if account_id.strip()
                            }
                        )
                    )
                    .exists()
                    .root_plan_id
                )
                # custom code
                arguments = line._get_analytic_distribution_arguments(root_plans)
                arguments["team_id"] = line.move_id.team_id.id
                arguments = frozendict(arguments)
                # custom code end here
                if arguments not in cache:
                    cache[arguments] = self.env[
                        "account.analytic.distribution.model"
                    ]._get_distribution(arguments)
                line.analytic_distribution = (
                    related_distribution | cache[arguments]
                    or line.analytic_distribution
                )
