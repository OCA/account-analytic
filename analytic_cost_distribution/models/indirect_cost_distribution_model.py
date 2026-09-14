# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IndirectCostDistributionModel(models.Model):
    _name = "indirect.cost.distribution.model"
    _description = "Indirect Cost Distribution Model"

    name = fields.Char(
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    active = fields.Boolean(
        default=True,
        help="Set active to false to hide the distribution model "
        "without removing it.",
    )
    distribution_method = fields.Selection(
        [
            ("timesheet", "Based on Timesheet"),
            ("profits", "Based on Profits"),
        ],
        default="timesheet",
        required=True,
        help="Method used to calculate the distribution proportion:\n"
        "- Based on Timesheet: distribute proportionally to timesheet hours "
        "registered in profit centres.\n"
        "- Based on Profits: distribute proportionally to profits "
        "(positive amounts) registered in profit centres.",
    )
    allowed_indirect_cost_plan_ids = fields.One2many(
        comodel_name="account.analytic.plan",
        compute="_compute_allowed_plan_ids",
    )
    allowed_profit_centre_plan_ids = fields.One2many(
        comodel_name="account.analytic.plan",
        compute="_compute_allowed_plan_ids",
    )
    indirect_cost_plan_ids = fields.Many2many(
        "account.analytic.plan",
        "indirect_cost_distribution_model_indirect_plan_rel",
        "distribution_model_id",
        "plan_id",
        string="Indirect Cost Plans",
        help="Analytic plans containing indirect costs to be distributed. "
        "These plans must be under the indirect costs root plan "
        "configured in company settings.",
    )
    profit_centre_plan_ids = fields.Many2many(
        "account.analytic.plan",
        "indirect_cost_distribution_model_profit_plan_rel",
        "distribution_model_id",
        "plan_id",
        string="Profit Centre Plans",
        help="Analytic plans representing profit centres where costs "
        "will be distributed. These plans must be under the profit "
        "centres root plan configured in company settings.",
    )

    @api.depends(
        "company_id",
        "company_id.indirect_costs_root_plan_ids",
        "company_id.profit_centres_root_plan_ids",
    )
    def _compute_allowed_plan_ids(self):
        for record in self:
            company = record.company_id or self.env.company
            record.allowed_indirect_cost_plan_ids = self._plans_under_roots(
                company.indirect_costs_root_plan_ids
            )
            record.allowed_profit_centre_plan_ids = self._plans_under_roots(
                company.profit_centres_root_plan_ids
            )

    @api.constrains("indirect_cost_plan_ids", "profit_centre_plan_ids", "company_id")
    def _check_plans_under_company_roots(self):
        for record in self:
            indirect_roots = record.company_id.indirect_costs_root_plan_ids
            profit_roots = record.company_id.profit_centres_root_plan_ids
            invalid_indirect = record.indirect_cost_plan_ids - self._plans_under_roots(
                indirect_roots
            )
            if invalid_indirect:
                raise ValidationError(
                    _(
                        "The following plans are not under the company "
                        "indirect-cost root plans: %s"
                    )
                    % ", ".join(invalid_indirect.mapped("display_name"))
                )
            invalid_profit = record.profit_centre_plan_ids - self._plans_under_roots(
                profit_roots
            )
            if invalid_profit:
                raise ValidationError(
                    _(
                        "The following plans are not under the company "
                        "profit-centre root plans: %s"
                    )
                    % ", ".join(invalid_profit.mapped("display_name"))
                )

    @api.model
    def _plans_under_roots(self, roots):
        if not roots:
            return self.env["account.analytic.plan"]
        return self.env["account.analytic.plan"].search([("id", "child_of", roots.ids)])

    def _get_plan_with_children(self, plan):
        """Return the plan and all its descendants."""
        return self.env["account.analytic.plan"].search([("id", "child_of", plan.ids)])

    def _get_all_indirect_cost_plans(self):
        self.ensure_one()
        return self._plans_under_roots(self.indirect_cost_plan_ids)

    def _get_all_profit_centre_plans(self):
        self.ensure_one()
        return self._plans_under_roots(self.profit_centre_plan_ids)

    def _get_indirect_cost_accounts(self):
        """Return all analytic accounts under indirect cost plans."""
        self.ensure_one()
        plans = self._get_all_indirect_cost_plans()
        return self.env["account.analytic.account"].search(
            [("plan_id", "in", plans.ids)]
        )

    def _get_profit_centre_accounts(self):
        """Return all analytic accounts under profit centre plans."""
        self.ensure_one()
        plans = self._get_all_profit_centre_plans()
        return self.env["account.analytic.account"].search(
            [("plan_id", "in", plans.ids)]
        )
