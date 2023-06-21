# Copyright 2015 ACSONE SA/NV
# Copyright 2020 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _prepare_invoice_line(self, line):
        """The method that allowed to add the analytic account to the invoice lines
        has been dropped in v13. Fortunately we can add it easily with this
        prepare method.
        """
        res = super()._prepare_invoice_line(line)
        analytic_account = line.order_id.session_id.config_id.account_analytic_id
        if analytic_account:
            res.update({"analytic_account_id": analytic_account.id})
        return res

    def action_pos_order_invoice(self):
        self_ctx = self.with_context(pos_analytic=True)
        return super(PosOrder, self_ctx).action_pos_order_invoice()
