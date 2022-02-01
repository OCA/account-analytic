# Copyright 2014 Acsone - Stéphane Bidoul <stephane.bidoul@acsone.eu>
# Copyright 2017 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestAccountAnalyticPlanRequired(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountAnalyticPlanRequired, cls).setUpClass()
        cls.account_obj = cls.env["account.account"]
        cls.account_type_obj = cls.env["account.account.type"]
        cls.move_obj = cls.env["account.move"]
        cls.move_line_obj = cls.env["account.move.line"]
        cls.analytic_account_obj = cls.env["account.analytic.account"]
        cls.analytic_tag_obj = cls.env["account.analytic.tag"]
        cls.user_type = cls.env.ref("account.data_account_type_revenue")
        cls.analytic_account_id = cls.analytic_account_obj.create(
            {
                "name": "test aa",
            }
        )
        cls.account_type = cls.account_type_obj.create(
            {"name": "Test account type", "type": "other", "internal_group": "equity"}
        )
        cls.account_id = cls.account_obj.create(
            {
                "name": "Test account",
                "code": "440000_demo",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.account_expense_id = cls.account_obj.create(
            {
                "name": "Other accoynt",
                "code": "600000_demo",
                "user_type_id": cls.env.ref("account.data_account_type_expenses").id,
                "reconcile": False,
            }
        )
        cls.analytic_distribution_id = cls.analytic_tag_obj.create(
            {
                "name": "test ad",
                "active_analytic_distribution": True,
            }
        )

    def _create_move(self, with_analytic, with_analytic_plan, amount=100):
        date = datetime.now()
        move_vals = {
            "journal_id": self.env["account.journal"]
            .search([("type", "=", "sale")])[0]
            .id,
            "date": date,
        }
        tags = False
        if with_analytic_plan:
            tags = [(6, 0, self.analytic_distribution_id.ids)]
        move_id = self.move_obj.create(move_vals)
        move_line_id = self.move_line_obj.with_context(
            check_move_validity=False
        ).create(
            {
                "move_id": move_id.id,
                "name": "/",
                "debit": 0,
                "credit": amount,
                "account_id": self.account_id.id,
                "analytic_account_id": self.analytic_account_id.id
                if with_analytic
                else False,
                "analytic_tag_ids": tags,
            }
        )
        self.move_line_obj.create(
            {
                "move_id": move_id.id,
                "name": "/",
                "debit": amount,
                "credit": 0,
                "account_id": self.account_expense_id.id,
            }
        )
        return move_line_id

    def test_optional(self):
        self._create_move(with_analytic=False, with_analytic_plan=False)
        self._create_move(with_analytic=True, with_analytic_plan=False)
        self._create_move(with_analytic=False, with_analytic_plan=True)

    def test_exclusive(self):
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=True, with_analytic_plan=True)

    def test_always_no_analytic(self):
        self.account_type.write(
            {
                "property_analytic_policy": "always",
            }
        )
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=False, with_analytic_plan=False)
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=False, with_analytic_plan=True)

    def test_always_no_analytic_0(self):
        # accept missing analytic account when debit=credit=0
        self.account_type.write(
            {
                "property_analytic_policy": "always",
            }
        )
        self._create_move(with_analytic=False, with_analytic_plan=False, amount=0)

    def test_always_with_analytic(self):
        self.account_type.write(
            {
                "property_analytic_policy": "always",
            }
        )
        self._create_move(with_analytic=True, with_analytic_plan=False)

    def test_always_plan_no_analytic_plan(self):
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan",
            }
        )
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=False, with_analytic_plan=False)
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=True, with_analytic_plan=False)

    def test_always_plan_no_analytic_plan_0(self):
        # accept missing analytic distribution when debit=credit=0
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan",
            }
        )
        self._create_move(with_analytic=False, with_analytic_plan=False, amount=0)

    def test_always_plan_with_analytic_plan(self):
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan",
            }
        )
        self._create_move(with_analytic=False, with_analytic_plan=True)

    def test_always_plan_or_account_nothing(self):
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan_or_account",
            }
        )
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=False, with_analytic_plan=False)

    def test_always_plan_or_account_no_analytic_plan_0(self):
        # accept missing analytic distribution when debit=credit=0
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan_or_account",
            }
        )
        self._create_move(with_analytic=False, with_analytic_plan=False, amount=0)
        self._create_move(with_analytic=True, with_analytic_plan=False, amount=0)
        self._create_move(with_analytic=False, with_analytic_plan=True, amount=0)

    def test_always_plan_or_account_with(self):
        self.account_id.user_type_id.write(
            {
                "property_analytic_policy": "always_plan_or_account",
            }
        )
        self._create_move(with_analytic=False, with_analytic_plan=True)
        self._create_move(with_analytic=True, with_analytic_plan=False)

    def test_never_no_analytic(self):
        self.account_type.write(
            {
                "property_analytic_policy": "never",
            }
        )
        self._create_move(with_analytic=False, with_analytic_plan=False)

    def test_never_with_analytic(self):
        self.account_type.write(
            {
                "property_analytic_policy": "never",
            }
        )
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=True, with_analytic_plan=False)
        with self.assertRaises(ValidationError):
            self._create_move(with_analytic=False, with_analytic_plan=True)

    def test_never_with_analytic_0(self):
        # accept analytic when debit=credit=0
        self.account_type.write(
            {
                "property_analytic_policy": "never",
            }
        )
        self._create_move(with_analytic=True, with_analytic_plan=False, amount=0)
        self._create_move(with_analytic=False, with_analytic_plan=True, amount=0)

    def test_always_remove_analytic_plan(self):
        # remove analytic plan account when policy is always
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan",
            }
        )
        line_id = self._create_move(with_analytic=False, with_analytic_plan=True)
        with self.assertRaises(ValidationError):
            line_id.write({"analytic_tag_ids": [(6, 0, [])]})

    def test_change_account(self):
        self.account_type.write(
            {
                "property_analytic_policy": "always_plan",
            }
        )
        # change account to a_expense with policy always_plan but missing
        # analytic distribution
        with self.assertRaises(ValidationError):
            line_id = self._create_move(with_analytic=False, with_analytic_plan=False)
            line_id.write({"account_id": self.account_expense_id.id})
        # change account to a_expense with policy always_plan
        # with analytic distribution -> ok
        self.move_line_obj.write(
            {
                "account_id": self.account_expense_id.id,
                "analytic_tag_ids": self.analytic_distribution_id.id,
            }
        )
