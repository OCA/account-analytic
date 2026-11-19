#  Copyright (c) 2025 Groupe Voltaire
#  @author Guillaume MASSON <guillaume.masson@groupevoltaire.com>
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends(
        "product_id",
        "account_id",
        "partner_id",
        "move_id.team_id",
    )
    def _compute_analytic_distribution(self):
        """
        Orchestrates the analytic distribution computation by grouping lines
        by their sales team and calling the super method with a specific context.
        """
        lines_by_team = defaultdict(lambda: self.env["account.move.line"])
        for line in self:
            lines_by_team[line.move_id.team_id] |= line
        for team, lines in lines_by_team.items():
            if team:
                super(
                    AccountMoveLine, lines.with_context(team_id=team.id)
                )._compute_analytic_distribution()
            else:
                super(AccountMoveLine, lines)._compute_analytic_distribution()
        return True
