# Copyright 2024 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    analytic_org_id = fields.Many2one(
        "account.analytic.organization",
        string="Analytic Organization",
        domain=lambda self: [("company_id", "=", self.env.company.id)],
    )

    def _compute_display_name(self):
        for partner in self:
            if partner.analytic_org_id:
                partner.display_name = (
                    f"{partner.name} ({partner.analytic_org_id.name})"
                )
            else:
                partner.display_name = partner.name or ""
