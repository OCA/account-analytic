# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    department_ids = fields.Many2many(
        comodel_name="hr.department",
        string="Departments",
        domain="['|',('company_id', '=?', company_id),('company_id', '=', False)]",
    )
