# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id=group_id)
        res['account_analytic_id'] = order.project_id.id
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def need_procurement(self):
        # when sale is installed only, there is no need to create procurements,
        # so we must force procurement creation
        for line in self:
            if line.order_id.project_id:
                return True
            else:
                return super(SaleOrderLine, self).need_procurement()
