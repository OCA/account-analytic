# Copyright 2014 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from datetime import datetime

from odoo import exceptions
from odoo.tests import common


class TestAccountAnalyticRequired(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticRequired, cls).setUpClass()
        cls.account_obj = cls.env["account.account"]
        cls.move_obj = cls.env["account.move"]
        cls.move_line_obj = cls.env["account.move.line"]
        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.analytic_plan_obj = cls.env["account.analytic.plan"]
        cls.analytic_plan = cls.analytic_plan_obj.create({"name": "test aa plan"})
        cls.analytic_account_1 = cls.analytic_account_obj.create(
            {"name": "test aa 1 for distribution", "plan_id": cls.analytic_plan.id}
        )
        cls.analytic_account_2 = cls.analytic_account_obj.create(
            {"name": "test aa 2 for distribution", "plan_id": cls.analytic_plan.id}
        )
        cls.account_sales = cls.account_obj.create(
            {
                "code": "X1020",
                "name": "Product Sales - (test)",
                "account_type": "income",
            }
        )
        cls.account_recv = cls.account_obj.create(
            {
                "code": "X11002",
                "name": "Debtors - (test)",
                "reconcile": True,
                "account_type": "asset_receivable",
            }
        )
        cls.account_exp = cls.account_obj.create(
            {
                "code": "X2110",
                "name": "Expenses - (test)",
                "account_type": "expense",
            }
        )
        cls.sales_journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
            }
        )
        cls.analytic_distribution_1 = {
            str(cls.analytic_account_1.id): 50.0,
        }
        cls.analytic_distribution_2 = {
            str(cls.analytic_account_2.id): 50.0,
        }

    def _create_move(self, amount=100, **kwargs):
        with_analytic = kwargs.get("with_analytic")
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
                "analytic_distribution": self.analytic_distribution_1
                if with_analytic
                else {},
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
        account.analytic_policy = policy

    def test_optional(self):
        self._set_analytic_policy(False)
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
            line.write({"analytic_distribution": {}})

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
                "analytic_distribution": self.analytic_distribution_1,
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

    # -- full analytic distribution -------------------------------------
    def _set_full_distribution_required(self, required, account=None):
        if account is None:
            account = self.account_sales
        account.analytic_full_distribution_required = required

    def _second_plan_account(self):
        plan = self.analytic_plan_obj.create({"name": "test aa plan 2"})
        return self.analytic_account_obj.create(
            {"name": "test aa 3 for distribution", "plan_id": plan.id}
        )

    def test_partial_distribution_allowed_by_default(self):
        """The historical behaviour: the policy alone accepts 50%."""
        self._set_analytic_policy("always")
        line = self._create_move(with_analytic=True)
        self.assertEqual(sum(line.analytic_distribution.values()), 50.0)

    def test_partial_distribution_refused_when_full_is_required(self):
        self._set_analytic_policy("always")
        self._set_full_distribution_required(True)
        with self.assertRaises(exceptions.ValidationError):
            self._create_move(with_analytic=True)

    def test_complete_distribution_accepted(self):
        line = self._create_move(with_analytic=True)
        self._set_analytic_policy("always")
        self._set_full_distribution_required(True)
        line.write(
            {
                "analytic_distribution": {
                    str(self.analytic_account_1.id): 60.0,
                    str(self.analytic_account_2.id): 40.0,
                }
            }
        )
        self.assertEqual(sum(line.analytic_distribution.values()), 100.0)

    def test_each_plan_must_be_complete(self):
        """Two plans, each covering the amount: 200% in total, and valid."""
        other = self._second_plan_account()
        line = self._create_move(with_analytic=True)
        self._set_analytic_policy("always")
        self._set_full_distribution_required(True)
        line.write(
            {
                "analytic_distribution": {
                    str(self.analytic_account_1.id): 100.0,
                    str(other.id): 100.0,
                }
            }
        )
        self.assertEqual(len(line._analytic_distribution_by_root_plan()), 2)

    def test_one_incomplete_plan_is_enough_to_refuse(self):
        other = self._second_plan_account()
        line = self._create_move(with_analytic=True)
        self._set_analytic_policy("always")
        self._set_full_distribution_required(True)
        # Bring the line to a valid state before testing the refusal, so the
        # savepoint of assertRaises does not flush the previous 50%.
        line.write({"analytic_distribution": {str(self.analytic_account_1.id): 100.0}})
        with self.assertRaises(exceptions.ValidationError):
            line.write(
                {
                    "analytic_distribution": {
                        str(self.analytic_account_1.id): 100.0,
                        str(other.id): 50.0,
                    }
                }
            )

    def test_no_check_without_a_policy(self):
        """The flag alone does nothing: it qualifies an existing policy."""
        self._set_analytic_policy(False)
        self._set_full_distribution_required(True)
        self._create_move(with_analytic=True)

    def test_no_check_on_the_never_policy(self):
        self._set_analytic_policy("never")
        self._set_full_distribution_required(True)
        self._create_move(with_analytic=False)

    def test_posted_policy_only_checks_once_posted(self):
        self._set_analytic_policy("posted")
        self._set_full_distribution_required(True)
        line = self._create_move(with_analytic=True)
        self.assertEqual(line.move_id.state, "draft")
        with self.assertRaises(exceptions.ValidationError):
            line.move_id.action_post()

    def test_deleted_analytic_account_is_ignored(self):
        """A distribution pointing at a removed account must not crash."""
        line = self._create_move(with_analytic=True)
        line.write({"analytic_distribution": {"999999999": 100.0}})
        self.assertEqual(line._analytic_distribution_by_root_plan(), {})
