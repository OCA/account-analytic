# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _get_analytic_lines(self):
        """Put partner on generated analytic lines"""
        iml = super(AccountInvoice, self)._get_analytic_lines()
        for il in iml:
            for analytic_vals in il.get('analytic_lines', []):
                analytic_vals[2]['other_partner_id'] = (
                    self.partner_id.commercial_partner_id.id)
        return iml
