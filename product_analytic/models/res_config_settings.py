# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..models.account_move import GROUP_AUPAA


class AccountConfigSettings(models.TransientModel):

    _inherit = "res.config.settings"

    group_always_use_product_analytic_account = fields.Boolean(
        string="Always use product analytic account", implied_group=GROUP_AUPAA
    )
