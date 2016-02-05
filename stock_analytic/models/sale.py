# -*- coding: utf-8 -*-
# © 2013 Julius Network Solutions
# © 2015 Clear Corp
# © 2016 Andhitia Rama <andhitia.r@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_order_line_procurement(self, order,
                                        line, group_id=False,
                                        context=None):
        res = super(
            SaleOrder, self)._prepare_order_line_procurement(
                self.env.cr, self.env.user.id, order,
                line, group_id=group_id, context=context)
        if order.project_id:
            res['account_analytic_id'] = order.project_id.id
        return res


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    account_analytic_id = fields.Many2one(
        string='Analytic Account',
        comodel_name='account.analytic.account',
        )

    @api.model
    def _run_move_create(self, procurement, context=None):
        res = super(
            ProcurementOrder, self)._run_move_create(
                self.env.cr, self.env.user.id,
                procurement,  context=context)
        if procurement.account_analytic_id:
            res['account_analytic_id'] = procurement.account_analytic_id.id
        return res
