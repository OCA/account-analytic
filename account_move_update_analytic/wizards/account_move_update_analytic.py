# Copyright 2022 Le Filament
# Copyright 2022 Moduon - Eduardo de Miguel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from ..models.account_move_line import force_state_sentinel


class AccountMoveUpdateAnalytic(models.TransientModel):
    _name = "account.move.update.analytic.wizard"
    _description = "Account Move Update Analytic Account Wizard"

    line_id = fields.Many2one("account.move.line", string="Invoice line")
    product_id = fields.Many2one(related="line_id.product_id")
    account_id = fields.Many2one(related="line_id.account_id")
    move_type = fields.Selection(related="line_id.move_id.move_type")
    analytic_precision = fields.Integer(related="line_id.analytic_precision")
    current_analytic_distribution = fields.Json(
        related="line_id.analytic_distribution", string="Current Analytic Distribution"
    )
    company_id = fields.Many2one(related="line_id.company_id")
    analytic_distribution = fields.Json(string="New Analytic Distribution")

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        aml = self.env["account.move.line"].browse(active_id)
        rec.update(
            {
                "line_id": aml.id,
                "product_id": aml.product_id.id,
                "account_id": aml.account_id.id,
                "move_type": aml.move_id.move_type,
                "analytic_precision": aml.analytic_precision,
                "current_analytic_distribution": aml.analytic_distribution,
                "analytic_distribution": aml.analytic_distribution,
            }
        )
        return rec

    def update_analytic_lines(self):
        self.ensure_one()

        # force recreating lines with analytic taxes
        taxes_with_analytic = self.line_id.tax_ids.filtered("analytic")
        self.line_id.move_id.line_ids.filtered(
            lambda x: x.tax_line_id in taxes_with_analytic
        ).with_context(dynamic_unlink=True, force_delete=True).unlink()

        self.line_id.with_context(
            account_move_update_analytic=force_state_sentinel
        ).analytic_distribution = self.analytic_distribution
