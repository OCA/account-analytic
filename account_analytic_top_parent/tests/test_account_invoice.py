# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_account_A = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account_A"}
        )
        cls.analytic_account_AB = cls.env["account.analytic.account"].create(
            {
                "name": "test analytic_account_AB",
                "parent_id": cls.analytic_account_A.id,
            }
        )
        cls.analytic_account_ABC = cls.env["account.analytic.account"].create(
            {
                "name": "test analytic_account_AB",
                "parent_id": cls.analytic_account_AB.id,
            }
        )

    def test_top_parent_if_no_parent_returns_itself(self):
        self.assertEqual(
            self.analytic_account_A.top_parent_id, self.analytic_account_A.top_parent_id
        )

    def test_top_parent_if_parent(self):
        self.assertEqual(
            self.analytic_account_AB.top_parent_id, self.analytic_account_A
        )

    def test_top_parent_if_grand_parent(self):
        self.assertEqual(
            self.analytic_account_ABC.top_parent_id, self.analytic_account_A
        )
