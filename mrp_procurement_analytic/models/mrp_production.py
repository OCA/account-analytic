# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):

    _inherit = 'mrp.production'

    @api.multi
    def _generate_raw_move(self, bom_line, line_data):
        self.ensure_one()
        move = super(MrpProduction, self)._generate_raw_move(
            bom_line=bom_line, line_data=line_data)
        procurement = self.procurement_ids and self.procurement_ids[0] or False
        if procurement and procurement.account_analytic_id:
            move.write({
                'analytic_account_id': procurement.account_analytic_id.id
            })
        return move

    @api.multi
    def _generate_finished_moves(self):
        self.ensure_one()
        move = super(MrpProduction, self)._generate_finished_moves()
        procurement = self.procurement_ids and self.procurement_ids[0] or False
        if procurement and procurement.account_analytic_id:
            move.write({
                'analytic_account_id': procurement.account_analytic_id.id
            })
        return move
