# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account',
        domain=[('type', '!=', 'view')])

    @api.model
    def _get_po_line_values_from_proc(
            self, procurement, partner, company, schedule_date):
        res = super(ProcurementOrder, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        res['account_analytic_id'] = procurement.account_analytic_id.id
        return res

    @api.multi
    def make_po(self):
        obj = self.with_context(
            account_analytic_id=self.account_analytic_id.id)
        return super(ProcurementOrder, obj).make_po()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        account_analytic_id = context and context.get('account_analytic_id')
        if account_analytic_id:
            args.insert(0, ('account_analytic_id', '=', account_analytic_id))
        return super(PurchaseOrderLine, self).search(
            cr, uid, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
