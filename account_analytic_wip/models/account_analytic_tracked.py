# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticTrackedItem(models.AbstractModel):
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

        return {
            "analytic_id": ...,
            "product_id": ...,
            ...,
        }
        """
        self.ensure_one()
        return {}

    def _get_tracking_planned_qty(self):
        """
        To be extended by inheriting Model
        """
        return 0.0

    def set_tracking_item(self, update_planned=False, force=False):
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
            if not item.analytic_tracking_item_id or force:
                vals = item._prepare_tracking_item_values()
                item.analytic_tracking_item_id = vals and TrackingItem.create(vals)
                # The Product my be a Cost Type with child Products
                cost_rules = item.analytic_tracking_item_id.product_id.activity_cost_ids
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
