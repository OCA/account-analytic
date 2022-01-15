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
    def setUp(self):
        super(TestAccountAnalyticRecursion, self).setUp()

        self.analytic_account_obj = self.env["account.analytic.account"]
        self.analytic_line_obj = self.env["account.analytic.line"]
        self.partner1 = self.env.ref("base.res_partner_1")
        self.partner2 = self.env.ref("base.res_partner_2")
        self.analytic_parent1 = self.create_analytic_account(
            {"name": "parent aa", "code": "01", "partner_id": self.partner1.id}
        )
        self.analytic_son = self.create_analytic_account(
            {"name": "son aa", "code": "02", "parent_id": self.analytic_parent1.id}
        )
        self.analytic_parent2 = self.create_analytic_account(
            {"name": "parent2 aa", "code": "01", "partner_id": self.partner2.id}
        )
        self.analytic_parent3 = self.create_analytic_account(
            {"name": "parent3 aa", "code": "01", "partner_id": self.partner2.id}
        )
        self.analytic_son2 = self.create_analytic_account(
            {"name": "son aa", "code": "02", "parent_id": self.analytic_parent3.id}
        )
        self.create_analytic_line("Analytic line son", self.analytic_son, 50)
        self.create_analytic_line("Analytic line parent1", self.analytic_parent1, 100)
        self.create_analytic_line("Analytic line parent2", self.analytic_parent2, 50)
        self.create_analytic_line("Analytic line son2", self.analytic_son2, -50)
        self.assertEqual(
            self.analytic_parent1.debit, 0, "Analytic account in the debit side"
        )
        self.assertEqual(self.analytic_parent3.debit, 50)

    def create_analytic_account(self, values):
        if hasattr(self.analytic_account_obj, "_default_code"):
            values.pop("code")
        return self.analytic_account_obj.create(values)

    def create_analytic_line(self, name, analytic, amount):
        return self.analytic_line_obj.create(
            {"name": name, "amount": amount, "account_id": analytic.id}
        )

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

    def test_archive(self):
        self.analytic_parent1.toggle_active()
        self.assertEqual(self.analytic_son.active, False)
        self.analytic_parent1.toggle_active()
        self.assertEqual(self.analytic_son.active, False)
        self.analytic_parent1.toggle_active()
        with self.assertRaises(UserError):
            self.analytic_son.toggle_active()

    def test_name(self):
        display_name = "[%s] parent aa / son aa" % self.analytic_son.code
        self.assertEqual(self.analytic_son.complete_name, "parent aa / son aa")
        self.assertEqual(self.analytic_son.display_name, display_name)
