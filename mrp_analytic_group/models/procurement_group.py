# Copyright 2021 Open Source Integrators - Daniel Reis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
    )
