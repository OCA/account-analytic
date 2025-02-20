# Copyright (C) 2024 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = ["stock.quant", "analytic.mixin"]

    def _apply_inventory(self):
        res = super()._apply_inventory()
        for quant in self:
            quant.analytic_distribution = False

        return res

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        """Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param package_id: `stock.quant.package`
        :param package_dest_id: `stock.quant.package`
        :return: dict with all values needed to create a new `stock.move`
                 with its move line.
        """
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, package_id, package_dest_id
        )
        if self.analytic_distribution:
            res["analytic_distribution"] = self.analytic_distribution
        return res

    @api.model
    def _get_inventory_fields_write(self):
        """Returns a list of fields user can edit when they want to edit a quant
        in `inventory_mode`.
        """
        fields = super()._get_inventory_fields_write()
        fields += ["analytic_distribution"]
        return fields
