# -*- coding: utf-8 -*-
# Copyright 2017 PESOL (http://pesol.es)
#                Angel Moya (angel.moya@pesol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    def _select(self):
        select_str = super(AccountInvoiceReport, self)._select()
        for dimension in self.env['account.analytic.dimension'].search([]):
            select_str += ',sub.x_dimension_%s' % dimension.code
        return select_str

    def _sub_select(self):
        select_str = super(AccountInvoiceReport, self)._sub_select()
        for dimension in self.env['account.analytic.dimension'].search([]):
            select_str += ',ail.x_dimension_%s' % dimension.code
        return select_str

    def _group_by(self):
        group_by_str = super(AccountInvoiceReport, self)._group_by()
        for dimension in self.env['account.analytic.dimension'].search([]):
            group_by_str += ',ail.x_dimension_%s' % dimension.code
        return group_by_str
