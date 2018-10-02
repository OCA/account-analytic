# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class MrpProduction(models.Model):

    _inherit = 'procurement.order'

    @api.multi
    def _prepare_mo_vals(self, bom):
        self.ensure_one()
        res = super(MrpProduction, self)._prepare_mo_vals(bom=bom)
        if self.account_analytic_id:
            res.update({
                'analytic_account_id': self.account_analytic_id.id,
            })
        return res
