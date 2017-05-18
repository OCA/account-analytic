# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, exceptions, _

CONTRACT_TYPE = [
    ('sale', 'Sale'),
    ('purchase', 'Purchase')
]
STATES = [
    ('template', 'Template'),
    ('draft', 'New'),
    ('open', 'In Progress'),
    ('pending', 'To Renew'),
    ('close', 'Closed'),
    ('cancelled', 'Cancelled')
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

    state = fields.Selection(
        selection=STATES,
        string="Status",
        default='draft'
    )

    @api.multi
    def create_purchase_contract_item(self):
        """
        Function that creates the wizard that will open the options to
        create itens to the active contract
        :return: Wizard created
        """
        if not self.id:
            super(PurchaseAccountAnalyticAnalysis, self).create()
        context = dict(self.env.context)
        context.update({
            'default_contract_id': self.id,
        })
        form = self.env.ref(
            'purchase_contract_analysis.'
            'view_purchase_contract_itens_wizard',
            True
        )
        return {
            'view_type': 'form',
            'view_id': [form.id],
            'view_mode': 'form',
            'res_model': 'purchase.contract.itens.wizard',
            'views': [(form.id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

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
            if line.remaining > 0:
                val = {
                    'name': line.name,
                    'product_id': line.product_id.id,
                    'price': line.price,
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

    @api.multi
    def _check_exist_contract_purchase_order(self):
        teste = self.env['purchase.order'].search(
            [
                ("project_id", "=", self.id)
            ]
        )
        return teste

    @api.multi
    def return_to_draft(self):
        if not self._check_exist_contract_purchase_order():
            self.write({'state': 'draft'})
            return True
        raise exceptions.Warning(
            _("It's not possible to turn the state of the contract back to "
              "draft because existis purchase orders of this contract!")
        )
