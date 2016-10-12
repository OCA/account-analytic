# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.multi
    def create_analytic_lines(self):
        pass
