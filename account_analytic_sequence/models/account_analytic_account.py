# Copyright 2017 ACSONE SA/NV
# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    code = fields.Char(default=lambda self: self._default_code(), copy=False,)

    _sql_constraints = [
        (
            "code_uniq",
            "UNIQUE(code, company_id)",
            "Reference must be unique per Company!",
        ),
    ]

    @api.model
    def create(self, vals):
        if "code" not in vals:
            vals["code"] = self._default_code()
        return super().create(vals)

    @api.model
    def _default_code(self):
        return self.env["ir.sequence"].next_by_code("account.analytic.account.code")

    @api.model
    def _assign_default_codes(self):
        for aaa in self.with_context(active_test=False).search([("code", "=", False)]):
            aaa.code = self._default_code()
