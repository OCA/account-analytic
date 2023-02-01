# -*- coding: utf-8 -*-

from odoo import fields, models


class Department(models.Model):
    _inherit = "hr.department"

    analytic_account_ids = fields.One2many(
        string="Analytic Accounts",
        comodel_name="account.analytic.account",
        inverse_name="department_id",
    )
