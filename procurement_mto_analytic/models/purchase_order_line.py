# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _merge_in_existing_line(
            self, product_id, product_qty, product_uom, location_id, name,
            origin, values):
        # Do not merge into a line with a different analytic account

        res = super(PurchaseOrderLine, self)._merge_in_existing_line

        if not self.account_analytic_id:
            po_line_analytic_account = False
        else:
            po_line_analytic_account = self.account_analytic_id.id

        if values.get('account_analytic_id') != po_line_analytic_account:
            return False

        return res
