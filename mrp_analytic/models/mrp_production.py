# Copyright 2015 ForgeFlow - Jordi Ballester Alomar
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic Account"
    )
