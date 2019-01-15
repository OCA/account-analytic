# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    analytics_id = fields.Many2one(
        'account.analytic.plan.instance', 'Analytic distribution',
        readonly=True, states={'draft': [('readonly', False)]},
    )
