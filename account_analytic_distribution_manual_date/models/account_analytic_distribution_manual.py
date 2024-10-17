# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountAnalyticDistributionManual(models.Model):
    _inherit = "account.analytic.distribution.manual"

    start_date = fields.Date()
    end_date = fields.Date()
