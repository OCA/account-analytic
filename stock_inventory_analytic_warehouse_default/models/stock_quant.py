# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _get_inventory_move_values(
        self,
        qty,
        location_id,
        location_dest_id,
        package_id=False,
        package_dest_id=False,
    ):
        res = super()._get_inventory_move_values(
            qty=qty,
            location_id=location_id,
            location_dest_id=location_dest_id,
            package_id=False,
            package_dest_id=False,
        )
        distrib = location_dest_id.warehouse_id.analytic_distribution
        if distrib:
            res.update({"analytic_distribution": distrib})
        return res
