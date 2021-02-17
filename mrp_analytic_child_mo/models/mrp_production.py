# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def write(self, vals):
        res = super(MRPProduction, self).write(vals)
        for mrp_order in self:
            stock_move_ids = mrp_order.procurement_group_id.stock_move_ids
            procurement_id = stock_move_ids.created_production_id.procurement_group_id
            child_mo_ids = procurement_id.mrp_production_ids
            child_mo_ids.write({"analytic_account_id": mrp_order.analytic_account_id})
        return res
