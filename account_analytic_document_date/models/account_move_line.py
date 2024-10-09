# Copyright 2024 (APSL - Nagarro) Miquel Pascual, Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_analytic_lines(self):
        vals = super()._prepare_analytic_lines()
        for val in vals:
            if self.move_id.document_date:
                val.update({"document_date": self.move_id.document_date})
            else:
                val.update({"document_date": self.move_id.invoice_date})
        return vals
