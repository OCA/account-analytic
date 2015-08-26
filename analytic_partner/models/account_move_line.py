# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _prepare_analytic_line(self, obj_line):
        res = super(AccountMoveLine, self)._prepare_analytic_line(obj_line)
        res['other_partner_id'] = (
            obj_line.invoice.partner_id.commercial_partner_id.id)
        return res
