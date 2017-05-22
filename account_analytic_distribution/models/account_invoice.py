# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def inv_line_characteristic_hashcode(self, invoice_line):
        code = super(AccountInvoice, self).inv_line_characteristic_hashcode(
            invoice_line)
        hashcode = '%s-%s' % (
            code, invoice_line.get('analytic_distribution_id', 'False'))
        return hashcode

    @api.model
    def invoice_line_move_line_get(self):
        invoice_line_model = self.env['account.invoice.line']
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        for move_line_dict in res:
            if 'invl_id' in move_line_dict:
                line = invoice_line_model.browse(move_line_dict['invl_id'])
                move_line_dict['analytic_distribution_id'] = \
                    line.analytic_distribution_id.id
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res['analytic_distribution_id'] = line.get(
            'analytic_distribution_id', False)
        return res
