# -*- coding: utf-8 -*-
# © 2015 Eficent - Jordi Ballester Alomar
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account')
