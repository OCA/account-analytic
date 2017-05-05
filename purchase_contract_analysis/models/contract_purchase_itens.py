# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, exceptions, _


class ContractPurchaseItens(models.Model):
    _name = "contract.purchase.itens"

    name = fields.Char(string="Name", required=True)
    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    quantity = fields.Float(string="Quantity")
    expected = fields.Float(string="Expected", required=True)
    invoiced = fields.Float(string="Invoiced")
    to_invoice = fields.Float(string="To Invoice")
    remaining = fields.Float(string="Remaining")
    contract_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Contract",
        required=True
    )

    @api.multi
    def _verify_expected_value(self, expected_amount):
        if expected_amount < 1:
            return False
        return True

    @api.model
    def create(self, vals):
        if 'expected' not in vals or not \
                self._verify_expected_value(vals['expected']):
            raise exceptions.Warning(
                _("Expected value need to be filled!")
            )
        return super(ContractPurchaseItens, self).create(vals)

    @api.model
    def write(self, vals):
        if 'expected' in vals and not \
                self._verify_expected_value(vals['expected']):
            raise exceptions.Warning(
                _("Expected value need to be filled!")
            )
        return super(ContractPurchaseItens, self).write(vals)
