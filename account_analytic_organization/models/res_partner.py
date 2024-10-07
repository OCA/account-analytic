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

    def name_get(self):
        result = super(ResPartner, self).name_get()
        updated_result = []

        for partner_id, name in result:
            partner = self.browse(partner_id)
            if partner.analytic_org_id:
                name = f"{partner.name} ({partner.analytic_org_id.name})"
            else:
                name = partner.name or ""
            updated_result.append((partner_id, name))

        return updated_result
