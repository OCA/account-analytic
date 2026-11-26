# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move.line"

    def open_analytic_items(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "analytic.account_analytic_line_action_entries"
        )
        action["domain"] = [("move_line_id", "=", self.id)]
        return action
