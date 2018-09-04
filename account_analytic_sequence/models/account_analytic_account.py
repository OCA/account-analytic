# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):

    _inherit = 'account.analytic.account'

    code = fields.Char(
        default=lambda self: self._get_default_code())

    @api.model
    def _get_default_code(self):
        return self.env['ir.sequence'].next_by_code(
            'account.analytic.account.code')
