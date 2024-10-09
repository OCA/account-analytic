# Copyright 2024 (APSL - Nagarro) Miquel Pascual, Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.tests import TransactionCase


class TestAccountMoveDocumentDate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountMoveDocumentDate, cls).setUpClass()
        cls.account_move_model = cls.env["account.move"]

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@partner.com",
                "phone": "123456789",
            }
        )

        cls.analytic_plan_1 = cls.env["account.analytic.plan"].create(
            {
                "name": "Plan 1",
                "default_applicability": "unavailable",
                "company_id": False,
            }
        )

        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "Account 1", "plan_id": cls.analytic_plan_1.id}
        )

    def test_create_invoice_without_document_date(self):
        invoice = self.account_move_model.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [
                                (6, 0, [self.env["account.tax"].search([], limit=1).id])
                            ],
                            "analytic_distribution": {self.analytic_account_1.id: 100},
                        },
                    )
                ],
            }
        )

        invoice.action_post()

        self.assertEqual(invoice.document_date, invoice.invoice_date)

        # Confirms that the analytic line has the same document_date as the account.move
        analytic_line = self.env["account.analytic.line"].search(
            [("move_line_id", "in", invoice.line_ids.ids)], limit=1
        )
        self.assertEqual(invoice.document_date, analytic_line.document_date)

    def test_create_invoice_with_document_date(self):
        document_date = datetime.now().date() + timedelta(days=1)
        invoice = self.account_move_model.create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Product",
                            "quantity": 1,
                            "price_unit": 100.0,
                            "tax_ids": [
                                (6, 0, [self.env["account.tax"].search([], limit=1).id])
                            ],
                            "analytic_distribution": {self.analytic_account_1.id: 100},
                        },
                    )
                ],
                "document_date": document_date,
            }
        )

        invoice.action_post()

        self.assertEqual(invoice.document_date, document_date)
        self.assertNotEqual(invoice.invoice_date, invoice.document_date)

        # Confirms that the analytic line has the same document_date as the account.move
        analytic_line = self.env["account.analytic.line"].search(
            [("move_line_id", "in", invoice.line_ids.ids)], limit=1
        )
        self.assertEqual(invoice.document_date, analytic_line.document_date)
