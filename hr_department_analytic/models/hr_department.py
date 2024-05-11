# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrDepartment(models.Model):

    _inherit = "hr.department"

    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
    )
