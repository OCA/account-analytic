# Copyright 2024 (APSL - Nagarro) Miquel Pascual, Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    document_date = fields.Date(
        "Document Date", related="move_id.document_date", readonly=False
    )

    def reconcile_bank_line(self):
        self.ensure_one()
        res = super().reconcile_bank_line()
        self.move_id.document_date = self.document_date
        return res
