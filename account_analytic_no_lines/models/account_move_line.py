# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.model
    def _must_create_analytic_line(self, move_line):
        if not move_line.product_id:
            return False
        if not hasattr(move_line.product_id, 'expense_policy'):
            return False
        if move_line.product_id.expense_policy == 'no':
            return False
        return True

    @api.multi
    def create_analytic_lines(self):
        self = self.filtered(self._must_create_analytic_line)
        return super(AccountMoveLine, self).create_analytic_lines()
