# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def view_account_move_update_analytic_full(self):
        return self.env["ir.actions.actions"]._for_xml_id(
            "account_move_update_analytic.action_view_full_account_move_update_analytic"
        )
