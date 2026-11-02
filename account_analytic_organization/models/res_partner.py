# Copyright 2024 APSL - Nagarro
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    analytic_org_id = fields.Many2one(
        "account.analytic.organization",
        string="Analytic Organization",
        domain=lambda self: [("company_id", "=", self.env.company.id)],
    )

    @api.depends("analytic_org_id.name")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for partner in self.filtered("analytic_org_id"):
            # Keep the address lines (show_address context) after the name
            name, sep, address = partner.display_name.partition("\n")
            partner.display_name = (
                f"{name} ({partner.analytic_org_id.name}){sep}{address}"
            )
        return res
