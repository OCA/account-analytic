# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.onchange("team_id")
    def _onchange_team_analytic_tags(self):
        for rec in self:
            if (
                rec.team_id
                and rec.team_id.analytic_tag_ids
                and rec.invoice_line_ids
            ):
                rec.invoice_line_ids.update(
                    {
                        "analytic_tag_ids": [
                            (4, tag.id) for tag in rec.team_id.analytic_tag_ids
                        ]
                    }
                )
