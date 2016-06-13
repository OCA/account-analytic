# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _get_po_line_values_from_proc(
            self, procurement, partner, company, schedule_date):
        res = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        res['account_analytic_id'] = procurement.account_analytic_id.id
        return res

    @api.multi
    def make_po(self):
        # This is a trick to avoid the grouping without this key.
        obj = self.with_context(
            account_analytic_id=self.account_analytic_id.id)
        return super(ProcurementOrder, obj).make_po()
