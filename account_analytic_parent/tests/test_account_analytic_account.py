# Copyright 2017 ForgeFlow S.L.
# Copyright 2017 Luxim d.o.o.
# Copyright 2017 Matmoz d.o.o.
# Copyright 2017 Deneroteam.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import UserError

from odoo.addons.analytic.tests.common import AnalyticCommon


class TestAccountAnalyticRecursion(AnalyticCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.analytic_line_obj = cls.env["account.analytic.line"]
        cls.partner1 = cls._create_partner(name="Test Partner 1")
        cls.partner2 = cls._create_partner(name="Test Partner 2")
        cls.plan = cls.analytic_plan_1
        cls.plan2 = cls.analytic_plan_2
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
        # 3-level hierarchy: analytic_parent1 -> analytic_son -> analytic_grandchild
        cls.analytic_grandchild = cls.create_analytic_account(
            {
                "name": "grandchild aa",
                "code": "03",
                "parent_id": cls.analytic_son.id,
                "plan_id": cls.plan.id,
            }
        )
        # plan2 hierarchy: plan2_parent -> plan2_child
        cls.plan2_parent = cls.create_analytic_account(
            {
                "name": "plan2 parent aa",
                "code": "10",
                "partner_id": cls.partner1.id,
                "plan_id": cls.plan2.id,
            }
        )
        cls.plan2_child = cls.create_analytic_account(
            {
                "name": "plan2 child aa",
                "code": "11",
                "parent_id": cls.plan2_parent.id,
                "plan_id": cls.plan2.id,
            }
        )

        cls.create_analytic_line("Analytic line son", cls.analytic_son, 50)
        cls.create_analytic_line("Analytic line parent1", cls.analytic_parent1, 100)
        cls.create_analytic_line("Analytic line parent2", cls.analytic_parent2, 50)
        cls.create_analytic_line("Analytic line son2", cls.analytic_son2, -50)
        cls.create_analytic_line(
            "Analytic line grandchild", cls.analytic_grandchild, 25
        )
        cls.create_analytic_line("Analytic line plan2 parent", cls.plan2_parent, 200)
        cls.create_analytic_line("Analytic line plan2 child", cls.plan2_child, 80)

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
        self.assertEqual(
            self.analytic_grandchild.debit, 0, "Analytic account in the debit side"
        )

    def test_recursion(self):
        with self.assertRaises(UserError):
            self.analytic_parent1.write({"parent_id": self.analytic_son.id})
        # Deeper cycle: grandparent cannot become a child of its own grandchild
        with self.assertRaises(UserError):
            self.analytic_parent1.write({"parent_id": self.analytic_grandchild.id})
        # Recursion check also applies to plan2 hierarchy
        with self.assertRaises(UserError):
            self.plan2_parent.write({"parent_id": self.plan2_child.id})

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
        # parent1 aggregates own line (100) + son (50) + grandchild (25) = 175
        self.assertEqual(self.analytic_parent1.credit, 175, "Wrong amount")
        self.assertEqual(self.analytic_parent1.balance, 175, "Wrong amount")
        # son aggregates own line (50) + grandchild (25) = 75
        self.assertEqual(
            self.analytic_son.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_son.credit, 75, "Wrong amount")
        self.assertEqual(self.analytic_son.balance, 75, "Wrong amount")
        # grandchild has only its own line
        self.assertEqual(
            self.analytic_grandchild.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_grandchild.credit, 25, "Wrong amount")
        self.assertEqual(self.analytic_grandchild.balance, 25, "Wrong amount")
        self.assertEqual(
            self.analytic_parent2.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_parent2.credit, 50, "Wrong amount")
        self.assertEqual(self.analytic_parent2.balance, 50, "Wrong amount")
        self.assertEqual(self.analytic_parent3.debit, 50)
        self.assertEqual(self.analytic_parent3.credit, 0)
        self.assertEqual(self.analytic_parent3.balance, -50)
        # plan2_parent aggregates own line (200) + plan2_child (80) = 280
        self.assertEqual(self.plan2_parent.debit, 0)
        self.assertEqual(self.plan2_parent.credit, 280, "Wrong amount")
        self.assertEqual(self.plan2_parent.balance, 280, "Wrong amount")
        # plan2_child has only its own line
        self.assertEqual(self.plan2_child.debit, 0)
        self.assertEqual(self.plan2_child.credit, 80, "Wrong amount")
        self.assertEqual(self.plan2_child.balance, 80, "Wrong amount")

    def test_archive(self):
        self.analytic_parent1.action_archive()
        self.assertEqual(self.analytic_son.active, False)
        # Grandchild must also be archived when grandparent is archived
        self.assertEqual(self.analytic_grandchild.active, False)
        self.analytic_parent1.action_unarchive()
        self.assertEqual(self.analytic_son.active, False)
        self.assertEqual(self.analytic_grandchild.active, False)
        self.analytic_parent1.action_archive()
        with self.assertRaises(UserError):
            self.analytic_son.action_unarchive()
        # Grandchild cannot be unarchived while its parent (son) is archived
        with self.assertRaises(UserError):
            self.analytic_grandchild.action_unarchive()

    def test_name(self):
        # plan2 hierarchy name
        plan2_child_display = (
            f"[{self.plan2_child.code}] plan2 parent aa / plan2 child aa"
        )
        self.assertEqual(
            self.plan2_child.complete_name, "plan2 parent aa / plan2 child aa"
        )
        self.assertEqual(self.plan2_child.display_name, plan2_child_display)

        display_name = f"[{self.analytic_son.code}] parent aa / son aa"
        self.assertEqual(self.analytic_son.complete_name, "parent aa / son aa")
        self.assertEqual(self.analytic_son.display_name, display_name)
        # 3-level deep complete_name
        grandchild_display_name = (
            f"[{self.analytic_grandchild.code}] parent aa / son aa / grandchild aa"
        )
        self.assertEqual(
            self.analytic_grandchild.complete_name, "parent aa / son aa / grandchild aa"
        )
        self.assertEqual(self.analytic_grandchild.display_name, grandchild_display_name)
