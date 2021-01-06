# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class Department(models.Model):
    _inherit = "hr.department"

    analytic_account_ids = fields.One2many(
        comodel_name="account.analytic.account",
        inverse_name="department_id",
    )
