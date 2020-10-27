# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmTeam(models.Model):

    _inherit = "crm.team"

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag", string="Analytic Tags"
    )
