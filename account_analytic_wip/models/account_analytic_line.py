# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AnalyticLine(models.Model):
    """
    Analytic Lines should keep a link to the corresponding Tracking Item,
    so that it can report the corresponding WIP amounts.
    """

    _inherit = "account.analytic.line"

    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item", string="Tracking Item"
    )
    parent_id = fields.Many2one(
        "account.analytic.line", "Parent Analytic Item", ondelete="cascade"
    )
    child_ids = fields.One2many(
        "account.analytic.line", "parent_id", string="Related Analytic Items"
    )
    activity_cost_id = fields.Many2one(
        "activity.cost.rule", "Cost Rule Applied", ondelete="restrict"
    )

    @api.onchange("product_id", "product_uom_id", "unit_amount", "currency_id")
    def on_change_unit_amount(self):
        """ Do not set Amount on cost parent Analytic Items """
        super().on_change_unit_amount()
        if self.child_ids:
            self.amount = 0

    def _prepare_activity_cost_data(self, cost_type):
        """
        Return a dict with the values to create
        a new Analytic item for a Cost Type.
        """
        self.ensure_one()
        values = {
            "name": "{} / {}".format(
                self.name, cost_type.product_id.display_name or cost_type.name
            ),
            "activity_cost_id": cost_type.id,
            "product_id": cost_type.product_id.id,
            "unit_amount": self.unit_amount * cost_type.factor,
        }
        # Remove the link the the Project Task,
        # otherwise the cost lines would wrongly show as Timesheet
        if hasattr(self, "project_id"):
            values["project_id"] = None
        if hasattr(self, "task_id"):
            values["task_id"] = None
        return values

    def _set_tracking_item(self):
        """
        When creating a child Analytic Item,
        find the correct matching child Tracking Item
        """
        for analytic_item in self.filtered("parent_id.analytic_tracking_item_id"):
            tracking_items = analytic_item.parent_id.analytic_tracking_item_id.child_ids
            tracking_item = tracking_items.filtered(
                lambda x: x.product_id == analytic_item.product_id
            )
            analytic_item.analytic_tracking_item_id = tracking_item
            if not tracking_item:
                _logger.error(
                    "Analytic Item %s: could not find related Tracked Item",
                    analytic_item.display_name,
                )

    def _create_child_lines(self):
        """
        Find applicable Activity Cost Rules
        and create Analytic Lines for each of them.

        This is done copying the original Analytic Item
        to ensure all other fields are preserved on the new Item.
        """
        for analytic_parent in self.filtered("product_id.activity_cost_ids"):
            cost_ids = analytic_parent.product_id.activity_cost_ids
            if cost_ids:
                # Parent Cost Type amount must be zero
                # to avoid duplication with child cost type amounts
                analytic_parent.amount = 0
            for cost_product in cost_ids:
                cost_vals = analytic_parent._prepare_activity_cost_data(
                    cost_type=cost_product
                )
                cost_vals["parent_id"] = analytic_parent.id
                analytic_child = analytic_parent.copy(cost_vals)
                analytic_child.on_change_unit_amount()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._set_tracking_item()
        res._create_child_lines()
        return res

    def write(self, vals):
        """
        If Units are updated, also update the related cost Analytic Items
        """
        res = super().write(vals)
        if vals.get("unit_amount"):
            for analytic_child in self.mapped("child_ids"):
                cost_vals = analytic_child._prepare_activity_cost_data(
                    cost_type=analytic_child.activity_cost_id
                )
                analytic_child.write(cost_vals)
                analytic_child.on_change_unit_amount()
        return res
