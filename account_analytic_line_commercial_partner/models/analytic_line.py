# Copyright 2026 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="partner_id.commercial_partner_id",
        store=True,
        readonly=True,
    )
