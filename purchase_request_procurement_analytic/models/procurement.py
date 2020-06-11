# -*- coding: utf-8 -*-
# Copyright 2019 Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _prepare_purchase_request_line(self, pr):
        vals = super(ProcurementOrder, self)._prepare_purchase_request_line(pr)
        vals['analytic_account_id'] = self.account_analytic_id.id or False
        return vals
