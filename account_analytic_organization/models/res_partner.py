# Copyright 2023 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    analytic_org_id = fields.Many2one(
        "account.analytic.organization", string="Analytic Organization"
    )
