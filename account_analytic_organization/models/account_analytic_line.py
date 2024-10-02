# Copyright 2023 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    analytic_org = fields.Char(
        string="Analytic Organization",
        related="partner_id.analytic_org_id.name",
        store=True,
    )
