# Copyright 2014 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from odoo import exceptions
from odoo.tests import common


class TestAccountAnalyticRequired(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticRequired, cls).setUpClass()
        cls.account_obj = cls.env["account.account"]
        cls.move_obj = cls.env["account.move"]
        cls.move_line_obj = cls.env["account.move.line"]
        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.analytic_account = cls.analytic_account_obj.create({"name": "test aa"})
        cls.analytic_account_1 = cls.analytic_account_obj.create(
            {"name": "test aa 1 for distribution"}
        )
        cls.analytic_account_2 = cls.analytic_account_obj.create(
            {"name": "test aa 2 for distribution"}
        )
        cls.analytic_tag_obj = cls.env["account.analytic.tag"]
        cls.analytic_distribution_obj = cls.env["account.analytic.distribution"]
        cls.account_sales = cls.account_obj.create(
            {
                "code": "X1020",
                "name": "Product Sales - (test)",
                "user_type_id": cls.env.ref("account.data_account_type_revenue").id,
            }
        )
        cls.account_recv = cls.account_obj.create(
            {
                "code": "X11002",
                "name": "Debtors - (test)",
                "reconcile": True,
                "user_type_id": cls.env.ref("account.data_account_type_receivable").id,
            }
        )
        cls.account_exp = cls.account_obj.create(
            {
                "code": "X2110",
                "name": "Expenses - (test)",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
            }
        )
        cls.sales_journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
            }
        )
        cls.analytic_tag = cls.analytic_tag_obj.create(
            {
                "name": "Analytic tag for test",
                "company_id": cls.env.company.id,
                "active_analytic_distribution": True,
            }
        )
        cls.analytic_tag_wo_distribution = cls.analytic_tag_obj.create(
            {"name": "Analytic tag for test 2", "company_id": cls.env.company.id}
        )
        cls.analytic_distribution_line_1 = cls.analytic_distribution_obj.create(
            {
                "name": "Analytic distribution line 1",
                "account_id": cls.analytic_account_1.id,
                "tag_id": cls.analytic_tag.id,
                "percentage": 50.0,
            }
        )
        cls.analytic_distribution_line_2 = cls.analytic_distribution_obj.create(
            {
                "name": "Analytic distribution line 2",
                "account_id": cls.analytic_account_1.id,
                "tag_id": cls.analytic_tag.id,
                "percentage": 50.0,
            }
        )

    def _create_move(self, amount=100, **kwargs):
        with_analytic = kwargs.get("with_analytic")
        with_analytic_tag = kwargs.get("with_analytic_tag")
        date = datetime.now()
        ml_obj = self.move_line_obj.with_context(check_move_validity=False)
        move_vals = {"name": "/", "journal_id": self.sales_journal.id, "date": date}
        move = self.move_obj.create(move_vals)
        move_line = ml_obj.create(
            {
                "move_id": move.id,
                "name": "/",
                "debit": 0,
                "credit": amount,
                "account_id": self.account_sales.id,
                "analytic_account_id": self.analytic_account.id
                if with_analytic
                else False,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag.id, self.analytic_tag_wo_distribution.id])
                ]
                if with_analytic_tag
                else False,
            }
        )
        ml_obj.create(
            {
                "move_id": move.id,
                "name": "/",
                "debit": amount,
                "credit": 0,
                "account_id": self.account_recv.id,
            }
        )
        return move_line

    def _set_analytic_policy(self, policy, account=None):
        if account is None:
            account = self.account_sales
        account.user_type_id.property_analytic_policy = policy

    def test_optional(self):
        self._set_analytic_policy("optional")
        self._create_move(with_analytic=False)
        self._create_move(with_analytic=True)

    def test_always_no_analytic(self):
        self._set_analytic_policy("always")
        with self.assertRaises(exceptions.ValidationError):
            self._create_move(with_analytic=False)

    def test_always_no_analytic_0(self):
        # accept missing analytic account when debit=credit=0
        self._set_analytic_policy("always")
        self._create_move(with_analytic=False, amount=0)

    def test_always_with_analytic(self):
        self._set_analytic_policy("always")
        self._create_move(with_analytic=True)

    def test_never_no_analytic(self):
        self._set_analytic_policy("never")
        self._create_move(with_analytic=False)

    def test_never_with_analytic(self):
        self._set_analytic_policy("never")
        with self.assertRaises(exceptions.ValidationError):
            self._create_move(with_analytic=True)

    def test_never_with_analytic_0(self):
        # accept analytic when debit=credit=0
        self._set_analytic_policy("never")
        self._create_move(with_analytic=True, amount=0)

    def test_always_remove_analytic(self):
        # remove analytic when policy is always
        self._set_analytic_policy("always")
        line = self._create_move(with_analytic=True)
        with self.assertRaises(exceptions.ValidationError):
            line.write({"analytic_account_id": False})

    def test_change_account(self):
        self._set_analytic_policy("always", account=self.account_exp)
        line = self._create_move(with_analytic=False)
        # change account to a_expense with policy always but missing
        # analytic_account
        with self.assertRaises(exceptions.ValidationError):
            line.write({"account_id": self.account_exp.id})
        # change account to a_expense with policy always
        # with analytic account -> ok
        line.write(
            {
                "account_id": self.account_exp.id,
                "analytic_account_id": self.analytic_account.id,
            }
        )

    def test_posted_raise(self):
        self._set_analytic_policy("posted")
        line = self._create_move(with_analytic=False)
        move = line.move_id
        with self.assertRaises(exceptions.ValidationError):
            move.action_post()

    def test_posted_ok(self):
        self._set_analytic_policy("posted")
        line = self._create_move(with_analytic=True)
        move = line.move_id
        move.action_post()
        self.assertEqual(move.state, "posted")

    def test_exception_policy_for_analytic_distribution(self):
        self._set_analytic_policy("always")
        self._create_move(with_analytic=False, with_analytic_tag=True)
        self._set_analytic_policy("posted")
        line = self._create_move(with_analytic=False, with_analytic_tag=True)
        line.move_id.action_post()
        self._set_analytic_policy("never")
        with self.assertRaises(exceptions.ValidationError), self.cr.savepoint():
            self._create_move(with_analytic=False, with_analytic_tag=True)
