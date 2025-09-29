# Copyright 2022 Le Filament
# Copyright 2022 Moduon - Eduardo de Miguel
# Copyright 2024 (Nagarro - APSL) - Bernat Obrador
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveUpdateAnalytic(models.TransientModel):
    _name = "account.move.update.analytic.wizard"
    _description = "Account Move Update Analytic Account Wizard"
    _inherit = "analytic.mixin"

    line_id = fields.Many2one("account.move.line", string="Invoice line")
    product_id = fields.Many2one(related="line_id.product_id")
    account_id = fields.Many2one(related="line_id.account_id")
    move_type = fields.Selection(selection="_move_type_selection", readonly=True)
    company_id = fields.Many2one(
        comodel_name="res.company", string="Company", readonly=True
    )
    current_analytic_distribution = fields.Json(
        related="line_id.analytic_distribution", string="Current Analytic Distribution"
    )

    def _move_type_selection(self):
        return self.env["account.move"].fields_get(allfields=["move_type"])[
            "move_type"
        ]["selection"]

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        active_model = self.env.context.get("active_model", "account.move.line")
        if active_model == "account.move":
            moves = self.env["account.move"].browse(self.env.context.get("active_ids"))
            move_0 = moves[0]
            rec.update(
                {
                    "move_type": move_0.move_type,
                    "company_id": move_0.company_id.id,
                }
            )
        elif active_model == "account.move.line":
            aml = self.env["account.move.line"].browse(active_id)
            rec.update(
                {
                    "line_id": aml.id,
                    "product_id": aml.product_id.id,
                    "account_id": aml.account_id.id,
                    "move_type": aml.move_id.move_type,
                    "analytic_precision": aml.analytic_precision,
                    "company_id": aml.company_id.id,
                    "current_analytic_distribution": aml.analytic_distribution,
                    "analytic_distribution": aml.analytic_distribution,
                }
            )
        return rec

    def update_analytic_lines(self):
        self.ensure_one()
        # Validate if mandatory plans has 100%
        self.with_context(validate_analytic=True)._validate_distribution()
        if self.line_id:
            self.line_id.analytic_distribution = self.analytic_distribution
        else:
            moves = self.env["account.move"].browse(self.env.context.get("active_ids"))
            moves.invoice_line_ids.analytic_distribution = self.analytic_distribution
