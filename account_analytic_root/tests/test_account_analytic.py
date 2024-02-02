# Copyright 2015 Antiun Ingenieria - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env.ref("analytic.analytic_plan_departments")
        cls.analytic_account_A = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account_A", "plan_id": cls.plan.id}
        )
        cls.analytic_account_AB = cls.env["account.analytic.account"].create(
            {
                "name": "test analytic_account_AB",
                "parent_id": cls.analytic_account_A.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_account_ABC = cls.env["account.analytic.account"].create(
            {
                "name": "test analytic_account_AB",
                "parent_id": cls.analytic_account_AB.id,
                "plan_id": cls.plan.id,
            }
        )

    def test_root_if_no_parent_returns_itself(self):
        self.assertEqual(
            self.analytic_account_A, self.analytic_account_A.root_analytic_account_id
        )

    def test_root_if_parent(self):
        self.assertEqual(
            self.analytic_account_AB.root_analytic_account_id, self.analytic_account_A
        )

    def test_root_if_grand_parent(self):
        self.assertEqual(
            self.analytic_account_ABC.root_analytic_account_id, self.analytic_account_A
        )
