# Copyright 2015 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    pos_account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic Account"
    )
