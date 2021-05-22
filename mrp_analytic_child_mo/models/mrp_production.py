# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MRPProduction(models.Model):
    _inherit = "mrp.production"

    def _update_child_mo_analytic_account(self):
        for mrp_order in self:
            stock_move_ids = mrp_order.procurement_group_id.stock_move_ids
            procurement_id = stock_move_ids.created_production_id.procurement_group_id
            child_mo_ids = procurement_id.mrp_production_ids
            child_mo_ids.write({"analytic_account_id": mrp_order.analytic_account_id})

    def action_confirm(self):
        res = super().action_confirm()
        self.filtered("analytic_account_id")._update_child_mo_analytic_account()
        return res

    def write(self, vals):
        res = super(MRPProduction, self).write(vals)
        if "analytic_account_id" in vals:
            self._update_child_mo_analytic_account()
        return res
