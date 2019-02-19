# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        res = super(SaleOrderLine, self).\
            _prepare_procurement_values(group_id)
        res.update({
            'account_analytic_id':
                self.order_id.analytic_account_id.id,
        })
        return res

    @api.multi
    def _purchase_service_prepare_line_values(self, purchase_order,
                                              quantity=False):
        res = super(SaleOrderLine, self).\
            _purchase_service_prepare_line_values(
                purchase_order=purchase_order, quantity=quantity)
        res.update({
            'account_analytic_id':
                self.order_id.analytic_account_id.id,
        })
        return res
