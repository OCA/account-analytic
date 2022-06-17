# Copyright 2015 ACSONE SA/NV
# Copyright 2020 Tecnativa - David Vidal
# Copyright 2022 FactorLibre - Luis J. Salvatierra <luis.salvatierra@factorlibre.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _prepare_analytic_account(self, line):
        return line.order_id.session_id.config_id.account_analytic_id.id

    def action_pos_order_invoice(self):
        self_ctx = self.with_context(pos_analytic=True)
        return super(PosOrder, self_ctx).action_pos_order_invoice()

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        account_analytic = self._prepare_analytic_account(line)
        inv_line = super()._action_create_invoice_line(line=line, invoice_id=invoice_id)
        if account_analytic:
            # Force Analytic Account in case onchange method on product discard it.
            inv_line.account_analytic_id = account_analytic
        return inv_line
