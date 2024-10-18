# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    manual_distribution_id = fields.Many2one(
        comodel_name="account.analytic.distribution.manual",
        string="Analytic distribution manual",
    )
