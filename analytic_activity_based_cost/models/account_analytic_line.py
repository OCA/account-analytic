# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticLine(models.Model):
    """
    Analytic Lines should keep a link to the corresponding Tracking Item,
    so that it can report the corresponding WIP amounts.
    """

    _inherit = "account.analytic.line"

    parent_id = fields.Many2one(
        "account.analytic.line", "Parent Analytic Item", ondelete="cascade"
    )
    child_ids = fields.One2many(
        "account.analytic.line", "parent_id", string="Related Analytic Items"
    )
    activity_cost_id = fields.Many2one("activity.cost.rule", "Activity Cost Rule")

    # Quantity and Amount for Child Analytic Items
    # Uses differernt fields to avoid doubling when aggregating data
    unit_abcost = fields.Float(
        "Breakdown Quantity",
        compute="_compute_unit_abcost",
        store=True,
        help="Quantity set on child Analytic Items, rolled up to the parent",
    )
    amount_abcost = fields.Monetary(
        "Breakdown Amount",
        compute="_compute_amount_abcost",
        store=True,
        help="Amount on child Analytic Items, rolled up to the parent",
    )

    @api.depends("activity_cost_id.factor", "parent_id.unit_amount")
    def _compute_unit_abcost(self):
        """Compute Units for Activity Based costs"""
        for item in self:
            if item.parent_id:
                item.unit_abcost = (
                    item.activity_cost_id.factor * item.parent_id.unit_amount
                )
            else:
                item.unit_abcost = 0.0

    @api.depends(
        "activity_cost_id", "unit_abcost", "activity_cost_id.product_id.standard_price"
    )
    def _compute_amount_abcost(self):
        """Compute amount for child Analytic Items"""
        for item in self:
            if item.activity_cost_id and item.product_id:
                price_abcost = item.product_id.price_compute(
                    "standard_price", uom=item.product_id.uom_id
                )[item.product_id.id]
                item.amount_abcost = price_abcost * -1 * item.unit_abcost
            else:
                item.amount_abcost = 0.0

    def _prepare_activity_cost_data(self, cost_rule):
        """
        Return a dict with the values to create
        a new Analytic item for a Cost Type.
        """
        vals = {
            "name": "{} / {}".format(
                self.name, cost_rule.product_id.display_name or cost_rule.name
            ),
            "parent_id": self.id,
            "activity_cost_id": cost_rule.id,
            "product_id": cost_rule.product_id.id,
            "unit_amount": 0.0,
            "amount": 0.0,
        }
        # For Project related items, such as timesheets lines,
        # don't copy the Project and Task, so that child items don't show as timesheets
        if hasattr(self, "project_id"):
            vals["project_id"] = False
        if hasattr(self, "task_id"):
            vals["task_id"] = False
        return vals

    def _populate_abcost_lines(self):
        """
        Find applicable Activity Cost Rules
        and create Analytic Lines for each of them.

        This is done copying the original Analytic Item
        to ensure all other fields are preserved on the new Item.
        """
        for analytic_parent in self.filtered("product_id.activity_cost_ids"):
            for cost_rule in analytic_parent.product_id.activity_cost_ids:
                cost_vals = analytic_parent._prepare_activity_cost_data(cost_rule)
                analytic_parent.copy(cost_vals)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._populate_abcost_lines()
        return res
