# coding: utf-8
# Copyright (C) 2015 - 2016 DynApps <http://www.dynapps.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        res = super(PurchaseOrder, self)._prepare_inv_line(
            account_id, order_line)
        if order_line.analytic_distribution_id:
            res['analytic_distribution_id'] = \
                order_line.analytic_distribution_id.id
        return res
