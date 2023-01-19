# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        # Update MTO Manufacturing Orders with the Analytic Account set on Sales Orders
        # Uses the same logic as the method `_compute_mrp_production_count` in `sale_mrp`
        res = super(SaleOrder, self).action_confirm()
        data = self.env["procurement.group"].read_group(
            [("sale_id", "in", self.ids)], ["ids:array_agg(id)"], ["sale_id"]
        )
        sale_mrps_dict = dict()
        for item in data:
            procurement_groups = self.env["procurement.group"].browse(item["ids"])
            created_production = procurement_groups.stock_move_ids.created_production_id
            sale_mrps_dict[item["sale_id"][0]] = (
                created_production.procurement_group_id.mrp_production_ids
                | procurement_groups.mrp_production_ids
            )
        for sale in self:
            productions = sale_mrps_dict.get(sale.id)
            if productions:
                productions.write({"analytic_account_id": sale.analytic_account_id})
        return res
