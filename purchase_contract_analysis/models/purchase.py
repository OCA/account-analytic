# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ContractPurchase(models.Model):
    _inherit = "purchase.order"

    project_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract / Analytic',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)]
        }
    )
