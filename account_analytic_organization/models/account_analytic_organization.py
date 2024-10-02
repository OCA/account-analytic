# Copyright 2023 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticOrganization(models.Model):
    _name = "account.analytic.organization"
    _description = "Account Analytic Organization"

    name = fields.Char(required=True)
