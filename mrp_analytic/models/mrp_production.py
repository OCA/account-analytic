# Copyright 2015 ForgeFlow - Jordi Ballester Alomar
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
