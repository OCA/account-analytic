# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Default Analytic Account on Inventory Adjustment Line",
    )
    analytic_tag_ids = fields.Many2many(
        "account.analytic.tag",
        string="Default Analytic Tags on Inventory Adjustment Line",
    )
