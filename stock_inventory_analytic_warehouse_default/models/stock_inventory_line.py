# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockInventoryLine(models.Model):

    _inherit = "stock.inventory.line"

    def _get_default_analytic_account(self):
        """
        Get analytic account from warehouse if defined
        """
        location_id = self.env.context.get("default_location_id")
        if location_id:
            warehouse = self.env["stock.location"].browse(location_id).get_warehouse()
            if warehouse.account_analytic_id:
                return warehouse.account_analytic_id
        return super()._get_default_analytic_account()

    def _get_default_analytic_tags(self):
        """
        Get analytic tags from warehouse if defined
        """
        location_id = self.env.context.get("default_location_id")
        if location_id:
            warehouse = self.env["stock.location"].browse(location_id).get_warehouse()
            if warehouse.account_analytic_tag_ids:
                return warehouse.account_analytic_tag_ids
        return super()._get_default_analytic_tags()

    @api.model_create_multi
    def create(self, vals_list):
        """
        Get the default analytic account if inventory is set on multiple
        locations
        """
        for vals in vals_list:
            location_id = vals.get("location_id")
            analytic_id = vals.get("analytic_account_id")
            if location_id and not analytic_id:
                vals["analytic_account_id"] = (
                    self.with_context(default_location_id=location_id)
                    ._get_default_analytic_account()
                    .id
                )
        return super().create(vals_list)
