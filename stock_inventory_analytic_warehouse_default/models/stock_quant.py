# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        res = super()._get_inventory_move_values(
            qty=qty, location_id=location_id, location_dest_id=location_dest_id, out=out
        )
        warehouse = location_dest_id.get_warehouse()
        if warehouse:
            if warehouse.account_analytic_id:
                res.update({"analytic_account_id": warehouse.account_analytic_id.id})
            if warehouse.account_analytic_tag_ids:
                res.update(
                    {
                        "analytic_tag_ids": [
                            (6, 0, warehouse.account_analytic_tag_ids.ids)
                        ]
                    }
                )
        return res
