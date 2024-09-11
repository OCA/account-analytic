# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    parent_line_id = fields.Many2one(
        comodel_name="account.analytic.line",
        string="Origin",
        ondelete="cascade",
        readonly=True,
    )
    child_line_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="parent_line_id",
        string="Child Lines",
        readonly=True,
    )

    def action_edit_analytic_line(self):
        context = dict(self.env.context)
        context["form_view_initial_mode"] = "edit"
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "analytic.account_analytic_line_action_entries"
        )
        action["context"] = context
        action["views"] = [(False, "form")]
        action["res_id"] = self.id
        return action

    def action_split_analytic_line(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "account_analytic_line_split.analytic_line_split_wizard_action"
        )
        action["context"] = {
            "active_id": self.id,
            "amount": self.amount,
            "account_id": self.account_id.id,
        }
        return action
