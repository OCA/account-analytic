# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields

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
