# Copyright 2015 ACSONE SA/NV
# Copyright 2020 Tecnativa - David Vidal
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
