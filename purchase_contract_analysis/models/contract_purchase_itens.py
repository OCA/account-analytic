# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ContractPurchaseItens(models.Model):
    _name = "contract.purchase.itens"

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
