# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountAssetAsset(models.Model):
    _inherit = "account.asset.asset"

    analytic_account_id = fields.Many2one(
        string="Analytic account",
        comodel_name='account.analytic.account',
        domain="[('type', 'not in', ('view', 'template')), "
               "('state', 'not in', ('template', 'draft', "
               "'close', 'cancelled'))]")
