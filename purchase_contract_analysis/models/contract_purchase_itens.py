# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ContractPurchaseItens(models.Model):
    _name = "contract.purchase.itens"

    @api.multi
    def _get_purchase_orders_of_the_contract(self, record):
        sale_order_obj = self.env['purchase.order']
        return sale_order_obj.search(
            [
                ('project_id', '=', record.contract_id.id)
            ]
        )

    @api.multi
    def _get_purchase_orders_of_product(self, product_id, sale_order_ids):
        sale_order_line_obj = self.env['purchase.order.line']
        return sale_order_line_obj.search(
            [
                ('product_id', '=', product_id),
                ('order_id', 'in', sale_order_ids)
            ]
        )

    @api.depends('expected', 'quantity')
    @api.multi
    def _compute_remaining_amount(self):
        for record in self:
            # if record.expected:
                record.remaining = record.quantity - (
                    record.invoiced_qty
                )

    @api.depends('expected', 'contract_id', 'quantity')
    @api.multi
    def _compute_to_invoice_amount(self):
        for record in self:
            if record.expected and record.contract_id:
                sale_order_ids = self._get_purchase_orders_of_the_contract(
                    record
                )
                if sale_order_ids:
                    contract_sale_order_ids = \
                        self._get_purchase_orders_of_product(
                            record.product_id.id, sale_order_ids.ids
                        )
                    total = 0.0
                    qty = 0.0
                    for line in contract_sale_order_ids:
                        total += line.price_subtotal
                        qty += line.product_qty
                    record.to_invoice = total - record.invoiced
                    record.invoiced_qty = qty
                    record.remaining = record.quantity - qty

    @api.depends('product_id', 'quantity', 'price')
    @api.multi
    def _compute_expected_amount(self):
        for record in self:
            if record.product_id and record.quantity:
                record.expected = \
                    record.price * record.remaining + record.invoiced + \
                    record.to_invoice

    @api.depends('product_id', 'contract_id')
    @api.multi
    def _compute_invoiced_amount(self):
        for record in self:
            purchase_order_ids = self._get_purchase_orders_of_the_contract(
                record
            )
            purchase_order_names = []
            for purchase_order in purchase_order_ids:
                if purchase_order.name not in purchase_order_names:
                    purchase_order_names.append(purchase_order.name)
            purchase_invoices = self.env['account.invoice'].search(
                [
                    ('origin', 'in', purchase_order_names)
                ]
            )
            total = 0.0
            for purchase_invoice in purchase_invoices:
                for line in purchase_invoice.invoice_line:
                    if line.product_id.id == record.product_id.id:
                        total += line.price_subtotal
            record.invoiced = total

    name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    price = fields.Float(string="Price", required=True)
    quantity = fields.Float(string="Quantity", required=True)
    expected = fields.Float(
        string="Expected",
        compute=_compute_expected_amount,
        store=True
    )
    invoiced = fields.Float(
        string="Invoiced",
        compute=_compute_invoiced_amount
    )
    invoiced_qty = fields.Float(
        string="Invoiced Qty",
        compute=_compute_to_invoice_amount
    )
    to_invoice = fields.Float(
        string="To Invoice",
        compute=_compute_to_invoice_amount
    )
    remaining = fields.Float(
        string="Remaining Qty",
        compute=_compute_remaining_amount
    )
    contract_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Contract",
        required=True
    )
