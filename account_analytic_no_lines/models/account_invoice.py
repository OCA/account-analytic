# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        move_lines = super(AccountInvoice, self)\
            .finalize_invoice_move_lines(move_lines)
        if move_lines and len(move_lines[0]) > 2 and \
                'analytic_line_ids' in move_lines[0][2]:
            move_lines[0][2].pop('analytic_line_ids')
        return move_lines
