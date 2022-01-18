# Copyright 2015-2020 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    timesheet_ids = fields.One2many(
        comodel_name="account.analytic.line",
        inverse_name="other_partner_id",
        string="Timesheet activities",
    )
    timesheet_count = fields.Integer(
        string="Timesheet Activities Number",
        compute="_compute_timesheet_count",
        store=True,
    )

    @api.depends("timesheet_ids")
    def _compute_timesheet_count(self):
        groups = self.env["account.analytic.line"].read_group(
            [("other_partner_id", "in", self.ids), ("project_id", "!=", False)],
            ["other_partner_id"],
            ["other_partner_id"],
        )
        result = {
            data["other_partner_id"][0]: (data["other_partner_id_count"])
            for data in groups
        }
        for partner in self:
            partner.timesheet_count = result.get(partner.id, 0)
