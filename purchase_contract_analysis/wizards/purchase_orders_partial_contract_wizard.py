# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import api, models, fields


class PurchaseOrdersPartialContractWizard(models.TransientModel):
    _name = "purchase.order.partial.contract.wizard"

    line_ids = fields.One2many(
        comodel_name="purchase.order.partial.contract.line",
        inverse_name="wizard_id"
    )

    @api.multi
    def create_purchase_order(self):
        purchase_order_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        for line in self.line_ids:
            if line.quantity:
                onchange_partner = purchase_order_obj.onchange_partner_id(
                    line.contract_id.partner_id.id
                )
                purchase_order_vals = {
                    'partner_id': line.contract_id.partner_id.id,
                    'date_order': datetime.now(),
                    'project_id': line.contract_id.id,
                    'invoice_method': 'order',
                    'picking_type_id':
                        self.env.ref('stock.picking_type_in').id,
                    'location_id':
                        self.env.ref('stock.stock_location_stock').id,
                }
                purchase_order_vals.update(onchange_partner['value'])
                purchase_order = purchase_order_obj.create(purchase_order_vals)
                produto_stats = purchase_order_line_obj.onchange_product_id(
                    purchase_order.pricelist_id.id, line.product_id.id,
                    line.quantity, False, purchase_order.partner_id.id
                )
                purchase_order_line_obj.create(
                    {
                        'order_id': purchase_order.id,
                        'product_id': line.product_id.id,
                        'date_planned': produto_stats['value']['date_planned'],
                        'name': produto_stats['value']['name'],
                        'price_unit': produto_stats['value']['price_unit'],
                        'product_qty': produto_stats['value']['product_qty'],
                        'product_uom': produto_stats['value']['product_uom'],
                        'taxes_id': produto_stats['value']['taxes_id']
                    }
                )
        return {'type': 'ir.actions.act_window_close'}


class PurchaseOrdersPartialContractLine(models.TransientModel):
    _name = "purchase.order.partial.contract.line"

    wizard_id = fields.Many2one(
        comodel_name="purchase.order.partial.contract.wizard"
    )
    name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    quantity = fields.Float(string="Quantity")
    expected = fields.Float(string="Expected")
    invoiced = fields.Float(string="Invoiced")
    to_invoice = fields.Float(string="To Invoice")
    remaining = fields.Float(string="Remaining")
    contract_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Contract"
    )
