# -*- coding: utf-8 -*-
# © 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Analytic Account')
