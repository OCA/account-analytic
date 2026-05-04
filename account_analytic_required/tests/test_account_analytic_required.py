# Copyright 2014 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import Command, exceptions, fields

from odoo.addons.base.tests.common import BaseCommon


class TestAccountAnalyticRequired(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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
                "company_ids": [Command.set(cls.env.company.ids)],
            }
        )
        cls.account_recv = cls.account_obj.create(
            {
                "code": "X11002",
                "name": "Debtors - (test)",
                "reconcile": True,
                "account_type": "asset_receivable",
                "company_ids": [Command.set(cls.env.company.ids)],
            }
        )
        cls.account_exp = cls.account_obj.create(
            {
                "code": "X2110",
                "name": "Expenses - (test)",
                "account_type": "expense",
                "company_ids": [Command.set(cls.env.company.ids)],
            }
        )

        cls.sales_journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
                "company_id": cls.env.company.id,
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
        move_vals = {
            "move_type": "entry",
            "journal_id": self.sales_journal.id,
            "date": fields.Date.context_today(self.env.user),
            "line_ids": [
                Command.create(
                    {
                        "name": "/",
                        "debit": 0,
                        "credit": amount,
                        "account_id": self.account_sales.id,
                        "analytic_distribution": self.analytic_distribution_1
                        if with_analytic
                        else {},
                    }
                ),
                Command.create(
                    {
                        "name": "/",
                        "debit": amount,
                        "credit": 0,
                        "account_id": self.account_recv.id,
                    }
                ),
            ],
        }
        move = self.move_obj.create(move_vals)
        return move.line_ids.filtered(
            lambda line: line.account_id == self.account_sales
        )[:1]

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
