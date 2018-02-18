# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def inv_line_characteristic_hashcode(self, invoice_line):
        code = super(AccountInvoice, self).inv_line_characteristic_hashcode(
            invoice_line)
        hashcode = '%s-%s' % (
            code, invoice_line.get('analytic_distribution_id', 'False'))
        return hashcode

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if 'invl_id' in line:
            invl = self.invoice_line.browse(line['invl_id'])
            if invl.analytic_distribution_id:
                res['analytic_distribution_id'] = \
                    invl.analytic_distribution_id.id
        return res
