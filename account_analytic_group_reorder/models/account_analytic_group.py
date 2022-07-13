# Copyright 2022 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountAnalyticGroup(models.Model):
    _inherit = "account.analytic.group"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
