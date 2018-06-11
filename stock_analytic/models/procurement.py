# -*- coding: utf-8 -*-
# Copyright 2013 Julius Network Solutions
# Copyright 2015 Clear Corp
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class Procurement(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _get_stock_move_values(self):
        res = super(Procurement, self)._get_stock_move_values()
        analytic = self.account_analytic_id
        if analytic:
            res['analytic_account_id'] = analytic.id
        return res
