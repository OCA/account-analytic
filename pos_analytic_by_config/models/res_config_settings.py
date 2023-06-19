# Copyright 2023 CAMPTOCAMP SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        related="pos_config_id.account_analytic_id",
    )
