# Copyright 2022 Le Filament
# Copyright 2022 Moduon - Eduardo de Miguel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveUpdateAnalytic(models.TransientModel):
    _name = "account.move.update.analytic.wizard"
    _description = "Account Move Update Analytic Account Wizard"

    line_id = fields.Many2one("account.move.line", string="Invoice line")
    current_analytic_account_id = fields.Many2one(
        related="line_id.analytic_account_id", string="Current Analytic Account"
    )
    current_analytic_tag_ids = fields.Many2many(
        related="line_id.analytic_tag_ids", string="Current Analytic Tags"
    )
    company_id = fields.Many2one(related="line_id.company_id")
    new_analytic_account_id = fields.Many2one(
        "account.analytic.account", string="New Analytic Account", check_company=True
    )
    new_analytic_tag_ids = fields.Many2many(
        "account.analytic.tag", string="New Analytic Tags", check_company=True
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self.env.context.get("active_id", False)
        aml = self.env["account.move.line"].browse(active_id)
        rec.update(
            {
                "line_id": active_id,
                "current_analytic_account_id": aml.analytic_account_id.id,
                "new_analytic_account_id": aml.analytic_account_id.id,
                "current_analytic_tag_ids": [(6, 0, aml.analytic_tag_ids.ids or [])],
                "new_analytic_tag_ids": [(6, 0, aml.analytic_tag_ids.ids or [])],
                "company_id": aml.company_id.id,
            }
        )
        return rec

    def update_analytic_lines(self):
        self.ensure_one()
        self.line_id.analytic_line_ids.unlink()
        if self.user_has_groups("analytic.group_analytic_accounting"):
            self.line_id.analytic_account_id = self.new_analytic_account_id.id
        if self.user_has_groups("analytic.group_analytic_tags"):
            self.line_id.write(
                {"analytic_tag_ids": [(6, 0, self.new_analytic_tag_ids.ids)]}
            )
        if self.line_id.parent_state == "posted" and (
            self.new_analytic_account_id or self.new_analytic_tag_ids
        ):
            self.line_id.create_analytic_lines()

        return False
