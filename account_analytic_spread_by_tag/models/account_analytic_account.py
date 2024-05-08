# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    mapped_analytic_tag_ids = fields.Many2many(comodel_name="account.analytic.tag")
