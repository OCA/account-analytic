# Copyright 2016-2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import SavepointCase


class TestAccountAnalyticNoLines(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticNoLines, cls).setUpClass()

        # ENVIRONMENTS

        cls.account_account = cls.env["account.account"]
        cls.account_analytic_account = cls.env["account.analytic.account"]
        cls.account_analytic_line = cls.env["account.analytic.line"]
        cls.account_journal = cls.env["account.journal"]
        cls.account_move = cls.env["account.move"]
        cls.account_move_line = cls.env["account.move.line"]
        cls.date = date.today()

        # INSTANCES

        # Instance: user
        cls.user = cls.env.ref("base.res_partner_2")

        # Instance: accounts
        cls.account_440000 = cls.account_account.create(
            {
                "name": "Related companies",
                "code": "440000_demo",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.account_550001 = cls.account_account.create(
            {
                "name": "Bank",
                "code": "550001_demo",
                "user_type_id": cls.env.ref("account.data_account_type_liquidity").id,
                "reconcile": False,
            }
        )
        cls.account_600000 = cls.account_account.create(
            {
                "name": "Purchasing raw materials",
                "code": "600000_demo",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "reconcile": False,
            }
        )

        # Analytic accounts
        cls.aa_1 = cls.account_analytic_account.create({"name": "AA 1"})
        cls.aa_2 = cls.account_analytic_account.create({"name": "AA 2"})

        # Invoice
        cls.invoice = cls.account_move.create(
            {
                "invoice_date": cls.date,
                "partner_id": cls.user.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 1",
                            "price_unit": 50,
                            "quantity": 2,
                            "account_id": cls.account_600000.id,
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
                            "account_id": cls.account_600000.id,
                            "analytic_account_id": cls.aa_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 3",
                            "price_unit": -100,
                            "quantity": 1,
                            "account_id": cls.account_600000.id,
                            "analytic_account_id": cls.aa_2.id,
                        },
                    ),
                ],
            }
        )
        cls.invoice_1 = cls.account_move.create(
            {
                "invoice_date": cls.date,
                "partner_id": cls.user.id,
                "move_type": "in_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test invoice line 4",
                            "price_unit": 1,
                            "quantity": 0,
                            "account_id": cls.account_600000.id,
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
        move_lines = self.account_move_line.search([("move_id", "=", self.invoice.id)])
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
        self.invoice.action_post()
        move_lines = self.account_move_line.search([("move_id", "=", self.invoice.id)])
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
        self.invoice_1.action_post()
        move_lines = self.account_move_line.search([("move_id", "=", self.invoice.id)])
        analytic_lines = self.account_analytic_line.search(
            [("move_id", "in", move_lines.ids)]
        ).ids
        self.assertFalse(analytic_lines)

    def test_gl_amounts(self):
        self.invoice.action_post()
        self.assertEqual(self.aa_1.gl_debit, 150)
        self.assertEqual(self.aa_1.gl_credit, 0)
        self.assertEqual(self.aa_1.gl_balance, -150)
        self.assertEqual(self.aa_2.gl_debit, 0)
        self.assertEqual(self.aa_2.gl_credit, 100)
        self.assertEqual(self.aa_2.gl_balance, 100)
