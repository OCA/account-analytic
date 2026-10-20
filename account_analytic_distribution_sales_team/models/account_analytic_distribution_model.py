#  Copyright (c) 2025 Groupe Voltaire
#  @author Guillaume MASSON <guillaume.masson@groupevoltaire.com>
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticDistributionModel(models.Model):
    _inherit = "account.analytic.distribution.model"

    team_id = fields.Many2one(
        comodel_name="crm.team",
        string="Sales Team",
        ondelete="cascade",
        help="Select a sales team for this distribution model to be applied"
        " automatically to invoice lines.",
    )

    def _get_distribution(self, vals):
        team_id = self.env.context.get("team_id")
        if team_id:
            vals["team_id"] = team_id
        res = super()._get_distribution(vals)
        return res
