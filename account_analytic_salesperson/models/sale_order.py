# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def _create_analytic_account(self, prefix=None):
        """Propagate sale order salesperson through context key"""
        for order in self:
            order = order.with_context(analytic_user_id=order.user_id.id)
            super(SaleOrder, order)._create_analytic_account(prefix=prefix)

    @api.multi
    def _action_confirm(self):
        """Ensure analytic account is created after sale order confirmation"""
        res = super()._action_confirm()
        for order in self:
            if not order.analytic_account_id:
                order._create_analytic_account()
        return res
