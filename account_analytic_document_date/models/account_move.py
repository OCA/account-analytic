# Copyright 2024 (APSL - Nagarro) Miquel Pascual, Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    document_date = fields.Date()

    @api.onchange("invoice_date")
    def _onchange_invoice_date(self):
        for record in self:
            if not record.document_date:
                record.document_date = record.invoice_date

    def action_post(self):
        res = super().action_post()
        if not self.document_date:
            self.document_date = self.invoice_date
        return res
