# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseRequestLineMakePurchaseOrder(models.TransientModel):
    _inherit = "purchase.request.line.make.purchase.order"

    @api.model
    def _prepare_purchase_order_line(self, po, item):
        vals = super()._prepare_purchase_order_line(po, item)
        vals["analytic_tag_ids"] = [(4, x.id) for x in item.line_id.analytic_tag_ids]
        return vals
