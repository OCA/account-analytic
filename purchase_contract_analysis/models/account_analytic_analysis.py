# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields

CONTRACT_TYPE = [
    ('sale', 'Sale'),
    ('purchase', 'Purchase')
]


class PurchaseAccountAnalyticAnalysis(models.Model):
    _inherit = "account.analytic.account"

    contract_purchase_itens_lines = fields.One2many(
        comodel_name='contract.purchase.itens',
        inverse_name='contract_id',
    )

    contract_type = fields.Selection(
        selection=CONTRACT_TYPE,
        string="Contract Type"
    )

    @api.multi
    def create_purchase_orders_wizard(self):
        """
        Function that creates the wizard that will open the options of contract
        lines and the quantity of this lines user want to create the purchase
        orders
        :return: Wizard created
        """
        wizard_obj = self.env['purchase.order.partial.contract.wizard']
        line_values = []
        for line in self.contract_purchase_itens_lines:
            val = {
                'name': line.name,
                'product_id': line.product_id.id,
                'expected': line.expected,
                'invoiced': line.invoiced,
                'to_invoice': line.to_invoice,
                'remaining': line.remaining,
                'contract_id': line.contract_id.id,
            }
            line_values.append((0, 0, val))
        val_wizard = {
            'line_ids': line_values,
            'contract_id': self.id
        }
        wizard = wizard_obj.create(val_wizard)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.order.partial.contract.wizard',
            'res_id': wizard.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context,
        }
