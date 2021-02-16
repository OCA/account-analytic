# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.procurement_group_id.stock_move_ids.created_production_id.write(
                {"analytic_account_id": order.analytic_account_id}
            )
        return res
