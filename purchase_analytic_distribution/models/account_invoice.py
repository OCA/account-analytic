# -*- coding: utf-8 -*-
#  Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#  Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(
            line
        )
        res['analytic_distribution_id'] = line.analytic_distribution_id.id
        return res
