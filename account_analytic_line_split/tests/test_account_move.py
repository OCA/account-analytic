# Copyright 2024 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAccountMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountMove, cls).setUpClass()

        cls.account = cls.env["account.account"].create(
            {
                "code": "test_account_01",
                "name": "test account",
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
                "reconcile": True,
            }
        )
        cls.account_2 = cls.env["account.account"].create(
            {
                "code": "test_account_02",
                "name": "test account 2",
                "user_type_id": cls.env.ref("account.data_account_type_payable").id,
                "reconcile": True,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
            }
        )
        cls.analytic_line = cls.env["account.analytic.line"].create(
            {
                "name": "Test Analytic Line",
                "amount": 100,
                "account_id": cls.analytic_account.id,
            }
        )
        cls.account_move = cls.env["account.move"].create(
            {
                "name": "Test Move",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test Move Line",
                            "debit": 50,
                            "credit": 0,
                            "account_id": cls.account.id,
                            "analytic_account_id": cls.analytic_account.id,
                            "analytic_line_ids": [(6, 0, [cls.analytic_line.id])],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Test Move Line",
                            "debit": 0,
                            "credit": 50,
                            "account_id": cls.account_2.id,
                        },
                    ),
                ],
            }
        )

    def test_compute_analytic_line_ids(self):
        self.account_move._compute_analytic_line_ids()
        self.assertIn(self.analytic_line, self.account_move.analytic_line_ids)
