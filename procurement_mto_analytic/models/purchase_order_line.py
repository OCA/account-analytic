# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright Avoin.Systems

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _merge_in_existing_line(
            self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        """Do not merge into a line with a different analytic account"""
        res = super(PurchaseOrderLine, self)._merge_in_existing_line
        if values.get('account_analytic_id') != self.account_analytic_id.id:
            return False
        return res
