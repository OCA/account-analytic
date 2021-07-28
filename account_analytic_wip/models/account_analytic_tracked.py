# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AnalyticTrackedItem(models.AbstractModel):
    """
    Mixin to use on Models that generate WIp Analytic Items,
    and should be linked to Tracking Items.
    """

    _name = "account.analytic.tracked.mixin"
    _description = "Cost Tracked Mixin"

    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item",
        string="Tracking Item",
        ondelete="cascade",
        copy=False,
    )

    def _prepare_tracking_item_values(self):
        """
        To be implemented by inheriting models.
        Return a dict with the values to create the related Tracking Item.
        """
        self.ensure_one()
        return {}

    def _get_tracking_planned_qty(self):
        """
        Get the initial planned quantity.
        To be extended by inheriting Model
        """
        return 0.0

    def set_tracking_item(self, update_planned=False):
        """
        Create and set the related Tracking Item, where actuals will be accumulated to.
        The _prepare_tracking_item_values() provides the values used to create it.

        If the update_planned flag is set, the planned amount is updated.
        The _get_tracking_planned_qty() method provides the planned quantity.

        By default is is not set, and will be zero for new tracking items.

        Returns one Tracking Item record or an empty recordset.
        """
        TrackingItem = self.env["account.analytic.tracking.item"]
        for item in self:
            if not item.analytic_tracking_item_id:
                vals = item._prepare_tracking_item_values()
                if vals:
                    tracking_item = TrackingItem.create(vals)
                    item.analytic_tracking_item_id = tracking_item
                    # FIXME: remove this code, is is ABC logic, not WIP logic!
                    # The Product my be a Cost Type with child Products
                    cost_rules = (
                        item.analytic_tracking_item_id.product_id.activity_cost_ids
                    )
                    for cost_type in cost_rules.product_id:
                        child_vals = dict(vals)
                        child_vals.update(
                            {
                                "parent_id": item.analytic_tracking_item_id.id,
                                "product_id": cost_type.id,
                            }
                        )
                        TrackingItem.create(child_vals)

            if update_planned and item.analytic_tracking_item_id:
                planned_qty = item._get_tracking_planned_qty()
                tracking_item = item.analytic_tracking_item_id
                for subitem in tracking_item | tracking_item.child_ids:
                    qty = planned_qty if subitem.to_calculate else 0.0
                    unit_cost = subitem.product_id.standard_price
                    subitem.planned_amount = qty * unit_cost

    @api.model
    def create(self, vals):
        """
        New tracked records automatically create Tracking Items, if possible.
        """
        new = super().create(vals)
        new.set_tracking_item()
        return new

    def write(self, vals):
        """
        Tracked records automatically create Tracking Items, if possible.
        """
        res = super().write(vals)
        self.set_tracking_item()
        return res
