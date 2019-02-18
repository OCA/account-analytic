# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.multi
    def _prepare_purchase_order_line(self, product_id, product_qty,
                                     product_uom, values, po, supplier):
        res = super(StockRule, self)._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, supplier)
        res.update({
            'account_analytic_id':
                values.get('account_analytic_id', False)
        })
        return res

    def _make_po_get_domain(self, values, partner):
        res = super(StockRule, self)._make_po_get_domain(
            values, partner)
        res += (('order_line.account_analytic_id', '=',
                 values.get('account_analytic_id', False)),)
        return res
