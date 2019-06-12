# -*- coding: utf-8 -*-
# Copyright 2019 Abraham Anes - <abraham@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution'
    )
