# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from odoo.tests.common import SavepointCase


class TestAccountAnalyticNoLines(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # MODELS
        cls.account_analytic_account = cls.env["account.analytic.account"]
        cls.account_analytic_line = cls.env["account.analytic.line"]
        cls.account_move = cls.env["account.move"]
        # INSTANCES
        # Partners
        cls.partner_01 = cls.env.ref("base.res_partner_2")
        # Analytic accounts
        cls.aa_1 = cls.account_analytic_account.create({"name": "AA 1"})
        cls.aa_2 = cls.account_analytic_account.create({"name": "AA 2"})
        # Product
        cls.product_01 = cls.env.ref("product.product_product_16")
        # Invoices
        cls.invoice = cls.account_move.with_context(default_type="in_invoice").create(
            {
                "partner_id": cls.partner_01.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 1",
                            "price_unit": 50,
                            "quantity": 2,
                            "analytic_account_id": cls.aa_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 2",
                            "price_unit": 25,
                            "quantity": 2,
                            "analytic_account_id": cls.aa_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 3",
                            "product_id": cls.product_01.id,
                            "price_unit": -100,
                            "quantity": 1,
                            "analytic_account_id": cls.aa_2.id,
                        },
                    ),
                ],
            }
        )
        cls.invoice_1 = cls.account_move.with_context(default_type="in_invoice").create(
            {
                "partner_id": cls.partner_01.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 4",
                            "price_unit": 1,
                            "quantity": 0,
                            "analytic_account_id": cls.aa_2.id,
                        },
                    )
                ],
            }
        )

    def test_create_analytic_lines(self):
        """
        Test the expected result when the method 'create_analytic_lines' is
        called on an invoice.
        The expected result is that no analytic line has been created
        for this invoice.
        """
        move_lines = self.invoice.line_ids
        for line in move_lines:
            line.create_analytic_lines()
        analytic_lines = self.account_analytic_line.search(
            [("move_id", "in", move_lines.ids)]
        ).ids
        self.assertFalse(analytic_lines)

    def test_finalize_invoice_move_lines_1(self):
        """
        Test the expected result when the method 'finalize_invoice_move_lines'
        is called on an invoice.
        The expected result is that no analytic line has been created
        for this invoice.
        """
        self.invoice.post()
        move_lines = self.invoice.line_ids
        analytic_lines = self.account_analytic_line.search(
            [("move_id", "in", move_lines.ids)]
        ).ids
        self.assertFalse(analytic_lines)

    def test_finalize_invoice_move_lines_2(self):
        """
        Test the expected result when the method 'finalize_invoice_move_lines'
        is called on an invoice with only one line with quantity == 0.
        The expected result is that no analytic line has been created
        for this invoice.
        """
        self.invoice_1.post()
        move_lines = self.invoice.line_ids
        analytic_lines = self.account_analytic_line.search(
            [("move_id", "in", move_lines.ids)]
        ).ids
        self.assertFalse(analytic_lines)

    def test_gl_amounts_01(self):
        self.invoice.post()
        self.assertEqual(self.aa_1.gl_debit, 150)
        self.assertEqual(self.aa_1.gl_credit, 0)
        self.assertEqual(self.aa_1.gl_balance, -150)
        self.assertEqual(self.aa_2.gl_debit, 0)
        self.assertEqual(self.aa_2.gl_credit, 100)
        self.assertEqual(self.aa_2.gl_balance, 100)

    def test_gl_amounts_02(self):
        self.invoice.post()
        self.assertEqual(
            self.aa_1.with_context(to_date=date.today() - timedelta(days=1)).gl_debit,
            0,
        )
        self.assertEqual(
            self.aa_1.with_context(from_date=date.today() + timedelta(days=1)).gl_debit,
            0,
        )
