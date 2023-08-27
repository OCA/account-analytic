# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    analytic_tracking_item_id = fields.Many2one(
        "account.analytic.tracking.item", string="Tracking Item", copy=False
    )

    def _prepare_tracking_item_values(self):
        return {
            "analytic_id": self.account_id.id,
            "product_id": self.product_id.id,
        }

    def _get_tracking_item(self):
        self.ensure_one()
        all_tracking = self.account_id.analytic_tracking_item_ids
        tracking = all_tracking.filtered(
            lambda x: x.product_id == self.product_id
            or (not self.product_id and not x.product_id)
        )
        return tracking

    def _get_set_tracking_item(self):
        """
        Given an Analytic Item,
        locate the corresponding Tracking Item
        and set it on the record.
        If the (parent level) Tracking Item does not exist, it is created.
        """
        tracking = self._get_tracking_item()
        if tracking:
            self.analytic_tracking_item_id = tracking
        elif not self.parent_id:
            # New Tracking Item created for parent Analytic Item only
            # This trigger automatic creation of child breakdown,
            # and we need to ensure these childs are also mapped to tracking items
            vals = self._prepare_tracking_item_values()
            tracking = self.env["account.analytic.tracking.item"].create(vals)
            self.analytic_tracking_item_id = tracking
            for item in self.child_ids:
                item._get_set_tracking_item()
        return tracking

    def populate_tracking_items(self):
        """
        When creating an Analytic Item,
        link it to a Tracking Item, the may have to be created if it doesn't exist.

        Use this (and used dependency methods) as a template for other models
        implementing related tracking items.
        """
        for item in self.filtered(lambda x: not x.analytic_tracking_item_id):
            item._get_set_tracking_item()

    @api.model_create_multi
    def create(self, vals_list):
        new = super().create(vals_list)
        new.populate_tracking_items()
        return new
