# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestAccountAnalyticRecursion(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.analytic_line_obj = cls.env["account.analytic.line"]
        cls.partner1 = cls.env["res.partner"].create({"name": "Test Partner 1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Test Partner 2"})
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.analytic_parent1 = cls.create_analytic_account(
            {
                "name": "parent aa",
                "code": "01",
                "partner_id": cls.partner1.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_son = cls.create_analytic_account(
            {
                "name": "son aa",
                "code": "02",
                "parent_id": cls.analytic_parent1.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_parent2 = cls.create_analytic_account(
            {
                "name": "parent2 aa",
                "code": "01",
                "partner_id": cls.partner2.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_parent3 = cls.create_analytic_account(
            {
                "name": "parent3 aa",
                "code": "01",
                "partner_id": cls.partner2.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.analytic_son2 = cls.create_analytic_account(
            {
                "name": "son aa",
                "code": "02",
                "parent_id": cls.analytic_parent3.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.create_analytic_line("Analytic line son", cls.analytic_son, 50)
        cls.create_analytic_line("Analytic line parent1", cls.analytic_parent1, 100)
        cls.create_analytic_line("Analytic line parent2", cls.analytic_parent2, 50)
        cls.create_analytic_line("Analytic line son2", cls.analytic_son2, -50)

    @classmethod
    def create_analytic_account(self, values):
        if hasattr(self.analytic_account_obj, "_default_code"):
            values.pop("code")
        return self.analytic_account_obj.create(values)

    @classmethod
    def create_analytic_line(self, name, analytic, amount):
        return self.analytic_line_obj.create(
            {
                "name": name,
                "amount": amount,
                "account_id": analytic.id,
                "auto_account_id": analytic.id,
            }
        )

    def test_analytic_account_debit(self):
        self.assertEqual(
            self.analytic_parent1.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_parent3.debit, 50)

    def test_recursion(self):
        with self.assertRaises(UserError):
            self.analytic_parent1.write({"parent_id": self.analytic_son.id})

    def test_onchange(self):
        self.analytic_son._onchange_parent_id()
        self.assertEqual(
            self.analytic_son.partner_id.id,
            self.partner1.id,
            "Partner should not change",
        )
        self.analytic_son.write({"parent_id": self.analytic_parent2.id})
        self.analytic_son._onchange_parent_id()
        self.assertEqual(
            self.analytic_son.partner_id.id, self.partner2.id, "Partner should change"
        )

    def test_debit_credit_balance(self):
        self.assertEqual(self.analytic_parent1.credit, 150, "Wrong amount")
        self.assertEqual(self.analytic_parent1.balance, 150, "Wrong amount")
        self.assertEqual(
            self.analytic_son.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_son.credit, 50, "Wrong amount")
        self.assertEqual(self.analytic_son.balance, 50, "Wrong amount")
        self.assertEqual(
            self.analytic_parent2.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_parent2.credit, 50, "Wrong amount")
        self.assertEqual(self.analytic_parent2.balance, 50, "Wrong amount")
        self.assertEqual(self.analytic_parent3.debit, 50)
        self.assertEqual(self.analytic_parent3.credit, 0)
        self.assertEqual(self.analytic_parent3.balance, -50)

    def test_debit_credit_balance_other_plan(self):
        plan = self.env["account.analytic.plan"].create({"name": "Other Plan"})
        parent = self.create_analytic_account(
            {"name": "other parent", "code": "11", "plan_id": plan.id}
        )
        son = self.create_analytic_account(
            {
                "name": "other son",
                "code": "12",
                "parent_id": parent.id,
                "plan_id": plan.id,
            }
        )
        column = plan._column_name()
        self.assertNotEqual(column, "account_id")
        self.analytic_line_obj.create(
            {"name": "other son line", "amount": 100, column: son.id}
        )
        self.analytic_line_obj.create(
            {"name": "other parent line", "amount": -30, column: parent.id}
        )
        self.assertEqual(son.balance, 100)
        self.assertEqual(parent.credit, 100)
        self.assertEqual(parent.debit, 30)
        self.assertEqual(parent.balance, 70)

    def test_debit_credit_balance_date_filter(self):
        line = self.create_analytic_line("Old line son", self.analytic_son, 1000)
        line.date = "2000-01-01"
        # debit/credit do not depend on the context: drop the cached values
        self.env.invalidate_all()
        account = self.analytic_parent1.with_context(from_date="2001-01-01")
        self.assertEqual(account.credit, 150)
        self.env.invalidate_all()
        account = self.analytic_parent1.with_context(to_date="2000-12-31")
        self.assertEqual(account.credit, 1000)

    def test_archive(self):
        self.analytic_parent1.action_archive()
        self.assertEqual(self.analytic_son.active, False)
        self.analytic_parent1.action_unarchive()
        self.assertEqual(self.analytic_son.active, False)
        self.analytic_parent1.action_archive()
        with self.assertRaises(UserError):
            self.analytic_son.action_unarchive()

    def test_name(self):
        display_name = f"[{self.analytic_son.code}] parent aa / son aa"
        self.assertEqual(self.analytic_son.complete_name, "parent aa / son aa")
        self.assertEqual(self.analytic_son.display_name, display_name)

    def test_level(self):
        self.assertEqual(self.analytic_son.level, 0)
        self.assertEqual(self.analytic_parent2.level, 0)
        self.assertEqual(self.analytic_parent1.level, 1)
        self.assertEqual(self.analytic_parent3.level, 1)
        # Deepening the tree bumps the whole chain
        grandchild = self.create_analytic_account(
            {
                "name": "grandchild aa",
                "code": "03",
                "parent_id": self.analytic_son.id,
                "plan_id": self.plan.id,
            }
        )
        self.assertEqual(grandchild.level, 0)
        self.assertEqual(self.analytic_son.level, 1)
        self.assertEqual(self.analytic_parent1.level, 2)
        # Removing the deepest branch restores previous levels
        grandchild.unlink()
        self.assertEqual(self.analytic_son.level, 0)
        self.assertEqual(self.analytic_parent1.level, 1)
