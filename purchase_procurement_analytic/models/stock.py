# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model
    def _prepare_procurement_from_move(self):
        # This code is necessary to propagate account analytic account from
        # sale to purchase through procurement.
        res = super(StockMove, self)._prepare_procurement_from_move()
        res['account_analytic_id'] = self.procurement_id.account_analytic_id.id
        return res
