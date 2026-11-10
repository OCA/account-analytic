# Copyright 2026 Innovyou
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class IndirectCostDistributionOperation(models.Model):
    _name = "indirect.cost.distribution.operation"
    _description = "Indirect Cost Distribution Operation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"

    name = fields.Char(
        required=True,
        default="/",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
    )
    date_from = fields.Date(
        required=True,
        tracking=True,
        help="Start date of the period for indirect costs to distribute.",
    )
    date_to = fields.Date(
        required=True,
        tracking=True,
        help="End date of the period for indirect costs to distribute.",
    )
    distribution_date = fields.Date(
        required=True,
        tracking=True,
        help="Date to use for the created distributed analytic lines.",
    )
    distributed_line_ids = fields.One2many(
        "account.analytic.line",
        "indirect_cost_distribution_operation_id",
        string="Distributed Lines",
    )
    distributed_line_count = fields.Integer(
        compute="_compute_distributed_line_count",
    )
    line_ids = fields.One2many(
        "indirect.cost.distribution.operation.line",
        "operation_id",
        string="Distribution Lines",
    )
    notes = fields.Text()

    @api.depends("distributed_line_ids")
    def _compute_distributed_line_count(self):
        for record in self:
            record.distributed_line_count = len(record.distributed_line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code(
                        "indirect.cost.distribution.operation"
                    )
                    or "/"
                )
        return super().create(vals_list)

    def _check_plan_conflicts(self, distribution_models):
        """Raise if any indirect-cost plan is covered by more than one model."""
        plan_model_map = {}
        plan_models_map = {}
        for model in distribution_models:
            for plan in model._get_all_indirect_cost_plans():
                if plan.id in plan_model_map:
                    plan_models_map.setdefault(
                        plan.id, [plan_model_map[plan.id]]
                    ).append(model)
                else:
                    plan_model_map[plan.id] = model

        if not plan_models_map:
            return
        conflict_lines = []
        for plan_id, conflicting_models in plan_models_map.items():
            plan = self.env["account.analytic.plan"].browse(plan_id)
            model_names = ", ".join(m.name for m in conflicting_models)
            conflict_lines.append(
                _("- PLAN: %(plan)s\nMODELS: %(models)s")
                % {"plan": plan.display_name, "models": model_names}
            )
        raise UserError(
            _(
                "The following analytic plans are covered by multiple "
                "distribution models:\n\n%s"
            )
            % "\n\n".join(conflict_lines)
        )

    def _classify_indirect_lines(self, indirect_cost_lines, model_account_map):
        """Split lines into per-model buckets and return uncovered accounts."""
        uncovered_accounts = self.env["account.analytic.account"]
        lines_by_model = {}
        root_plans = self.company_id.indirect_costs_root_plan_ids
        for line in indirect_cost_lines:
            if not line.account_id:
                continue
            if line.account_id.id in model_account_map:
                model = model_account_map[line.account_id.id]
                lines_by_model.setdefault(model.id, []).append(line)
            elif root_plans and self._is_account_under_plans(
                line.account_id, root_plans
            ):
                uncovered_accounts |= line.account_id
        return lines_by_model, uncovered_accounts

    def action_compute(self):
        """Compute the distribution lines based on indirect costs in date range."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Operation must be in draft state to compute."))

        self.line_ids.unlink()

        distribution_models = self.env["indirect.cost.distribution.model"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("active", "=", True),
            ]
        )

        if not distribution_models:
            raise UserError(
                _("No active distribution models found for company %s.")
                % self.company_id.name
            )

        self._check_plan_conflicts(distribution_models)

        model_account_map = {}
        for model in distribution_models:
            for account in model._get_indirect_cost_accounts():
                model_account_map[account.id] = model

        indirect_cost_lines = self.env["account.analytic.line"].search(
            [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("company_id", "=", self.company_id.id),
                ("amount", "<", 0),
                ("distributed_by_operation_id", "=", False),
            ]
        )

        already_distributed_lines = self.env["account.analytic.line"].search(
            [
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
                ("company_id", "=", self.company_id.id),
                ("amount", "<", 0),
                ("distributed_by_operation_id", "!=", False),
            ]
        )

        lines_by_model, uncovered_accounts = self._classify_indirect_lines(
            indirect_cost_lines, model_account_map
        )

        if uncovered_accounts:
            raise UserError(
                _(
                    "The following analytic accounts have indirect costs but "
                    "are not covered by any distribution model:\n%s\n\n"
                    "Please add them to a distribution model before proceeding."
                )
                % "\n".join(f"- {a.name}" for a in uncovered_accounts)
            )

        line_vals = []
        for model_id, lines in lines_by_model.items():
            total_amount = sum(line.amount for line in lines)
            line_vals.append(
                {
                    "operation_id": self.id,
                    "distribution_model_id": model_id,
                    "source_amount": total_amount,
                    "source_line_ids": [(6, 0, [line.id for line in lines])],
                }
            )

        if line_vals:
            self.env["indirect.cost.distribution.operation.line"].create(line_vals)

        already_distributed_indirect = already_distributed_lines.filtered(
            lambda line: line.account_id.id in model_account_map
        )
        if already_distributed_indirect:
            ops = already_distributed_indirect.mapped("distributed_by_operation_id")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Warning"),
                    "message": _(
                        "Some indirect costs in this period have already been "
                        "distributed by other operations: %s. "
                        "These lines have been excluded from the current "
                        "computation."
                    )
                    % ", ".join(ops.mapped("name")),
                    "type": "warning",
                    "sticky": True,
                },
            }

        return True

    def _is_account_under_plans(self, account, root_plans):
        """Check whether an analytic account belongs to any of the root plans
        or their children."""
        plan = account.plan_id
        while plan:
            if plan.id in root_plans.ids:
                return True
            plan = plan.parent_id
        return False

    def action_distribute(self):
        """Create the distributed analytic lines."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Operation must be in draft state to distribute."))

        if not self.line_ids:
            raise UserError(_("No distribution lines found. Please compute first."))

        self.distributed_line_ids.unlink()

        all_line_vals = []
        all_source_lines = self.env["account.analytic.line"]
        for line in self.line_ids:
            all_line_vals.extend(
                line._prepare_distribution_lines(self.distribution_date)
            )
            all_source_lines |= line.source_line_ids

        if all_line_vals:
            self.env["account.analytic.line"].create(all_line_vals)

        all_source_lines.write({"distributed_by_operation_id": self.id})

        self.state = "done"
        return True

    def action_reset_to_draft(self):
        """Reset operation to draft and delete distributed lines."""
        self.ensure_one()
        source_lines = self.line_ids.mapped("source_line_ids")
        source_lines.write({"distributed_by_operation_id": False})
        self.distributed_line_ids.unlink()
        self.state = "draft"
        return True

    def action_view_distributed_lines(self):
        """Open view of distributed analytic lines."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Distributed Lines"),
            "res_model": "account.analytic.line",
            "view_mode": "list,form",
            "views": [
                (
                    self.env.ref("analytic.view_account_analytic_line_tree").id,
                    "list",
                ),
                (False, "form"),
            ],
            "search_view_id": [
                self.env.ref("analytic.view_account_analytic_line_filter").id,
                "search",
            ],
            "domain": [("indirect_cost_distribution_operation_id", "=", self.id)],
            "context": {
                "default_indirect_cost_distribution_operation_id": self.id,
            },
        }


class IndirectCostDistributionOperationLine(models.Model):
    _name = "indirect.cost.distribution.operation.line"
    _description = "Indirect Cost Distribution Operation Line"

    operation_id = fields.Many2one(
        "indirect.cost.distribution.operation",
        string="Operation",
        required=True,
        ondelete="cascade",
    )
    distribution_model_id = fields.Many2one(
        "indirect.cost.distribution.model",
        string="Distribution Model",
        required=True,
    )
    source_amount = fields.Float(
        help="Total amount of indirect costs from this distribution model.",
    )
    source_line_ids = fields.Many2many(
        "account.analytic.line",
        "indirect_cost_distribution_op_line_source_rel",
        "operation_line_id",
        "analytic_line_id",
        string="Source Lines",
    )

    def _get_distribution_proportions(self):
        """Return dict {account_id: proportion} for this line's model."""
        self.ensure_one()
        model = self.distribution_model_id
        if model.distribution_method == "profits":
            return self._get_profits_proportions()
        return self._get_timesheet_proportions()

    def _get_timesheet_proportions(self):
        self.ensure_one()
        model = self.distribution_model_id
        profit_accounts = model._get_profit_centre_accounts()

        if not profit_accounts:
            return {}

        timesheet_lines = self.env["account.analytic.line"].search(
            [
                ("date", ">=", self.operation_id.date_from),
                ("date", "<=", self.operation_id.date_to),
                ("account_id", "in", profit_accounts.ids),
                ("project_id", "!=", False),
            ]
        )

        hours_by_account = {}
        total_hours = 0.0
        for line in timesheet_lines:
            account_id = line.account_id.id
            hours = line.unit_amount or 0.0
            hours_by_account[account_id] = hours_by_account.get(account_id, 0.0) + hours
            total_hours += hours

        proportions = {}
        if total_hours > 0:
            for account_id, hours in hours_by_account.items():
                proportions[account_id] = hours / total_hours

        return proportions

    def _get_profits_proportions(self):
        self.ensure_one()
        model = self.distribution_model_id
        profit_accounts = model._get_profit_centre_accounts()

        if not profit_accounts:
            return {}

        profit_lines = self.env["account.analytic.line"].search(
            [
                ("date", ">=", self.operation_id.date_from),
                ("date", "<=", self.operation_id.date_to),
                ("account_id", "in", profit_accounts.ids),
                ("amount", ">", 0),
            ]
        )

        profits_by_account = {}
        total_profits = 0.0
        for line in profit_lines:
            account_id = line.account_id.id
            amount = line.amount or 0.0
            profits_by_account[account_id] = (
                profits_by_account.get(account_id, 0.0) + amount
            )
            total_profits += amount

        proportions = {}
        if total_profits > 0:
            for account_id, profits in profits_by_account.items():
                proportions[account_id] = profits / total_profits

        return proportions

    def _prepare_distribution_lines(self, distribution_date):
        """Prepare analytic line values for distribution."""
        self.ensure_one()
        line_vals = []
        proportions = self._get_distribution_proportions()

        if not proportions:
            return line_vals

        source_amount = self.source_amount  # already negative

        for account_id, proportion in proportions.items():
            distributed_amount = source_amount * proportion
            line_vals.append(
                {
                    "name": _("Cost distribution from %s")
                    % self.distribution_model_id.name,
                    "date": distribution_date,
                    "account_id": account_id,
                    "amount": distributed_amount,
                    "company_id": self.operation_id.company_id.id,
                    "indirect_cost_distribution_operation_id": (self.operation_id.id),
                    "indirect_cost_distribution_model_id": (
                        self.distribution_model_id.id
                    ),
                }
            )

        return line_vals
