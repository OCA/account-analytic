# Copyright 2023-2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


class TestHrExpenseAnalyticTagBase(TestExpenseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.analytic_tag_1 = aa_tag_model.create({"name": "Test tag 1"})
        cls.analytic_tag_2 = aa_tag_model.create({"name": "Test tag 2"})
        cls.expense = cls._create_expense(cls)

    def _create_expense(self):
        expense_form = Form(
            self.env["hr.expense"].with_context(
                default_product_id=self.product_a.id,
                default_employee_id=self.expense_employee.id,
            )
        )
        expense_form.name = "Test expense"
        return expense_form.save()

    def _action_post_expense(self):
        res = self.expense.action_post()
        if res:
            wizard = (
                self.env[res["res_model"]].with_context(**res["context"]).create({})
            )
            wizard.action_post_entry()

    @mute_logger("odoo.models.unlink")
    def _test_hr_expense_with_tag(self):
        """Tag without analytic accounts."""
        self.expense.analytic_distribution = {self.analytic_account_1.id: 100}
        self.expense.analytic_tag_ids = self.analytic_tag_1
        self.expense._do_approve(check=False)
        self._action_post_expense()
        move = self.expense.account_move_id
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    @mute_logger("odoo.models.unlink")
    def _test_hr_expense_with_tags_01(self):
        """Tags without analytic accounts."""
        self.expense.analytic_distribution = {self.analytic_account_1.id: 100}
        self.expense.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        self.expense._do_approve(check=False)
        self._action_post_expense()
        move = self.expense.account_move_id
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    @mute_logger("odoo.models.unlink")
    def _test_hr_expense_with_tags_02(self):
        """Tags with analytic account and expense analytic account 1 + 2."""
        self.analytic_tag_1.account_analytic_id = self.analytic_account_1
        self.analytic_tag_2.account_analytic_id = self.analytic_account_2
        self.expense.analytic_distribution = {
            self.analytic_account_1.id: 50,
            self.analytic_account_2.id: 50,
        }
        self.expense.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        self.expense._do_approve(check=False)
        self._action_post_expense()
        move = self.expense.account_move_id
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    @mute_logger("odoo.models.unlink")
    def _test_hr_expense_with_tags_03(self):
        """Tags with analytic account and expense analytic account 1."""
        self.analytic_tag_1.account_analytic_id = self.analytic_account_1
        self.analytic_tag_2.account_analytic_id = self.analytic_account_2
        self.expense.analytic_distribution = {
            self.analytic_account_1.id: 50,
        }
        self.expense.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        self.expense._do_approve(check=False)
        self._action_post_expense()
        move = self.expense.account_move_id
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    @mute_logger("odoo.models.unlink")
    def _test_hr_expense_without_tags(self):
        self.expense.analytic_distribution = {self.analytic_account_1.id: 100}
        self.expense._do_approve(check=False)
        self._action_post_expense()
        move = self.expense.account_move_id
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)


@tagged("-at_install", "post_install")
class TestHrExpenseAnalyticTagOwnAccount(TestHrExpenseAnalyticTagBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.expense.payment_mode = "own_account"

    def test_hr_expense_with_tag(self):
        self._test_hr_expense_with_tag()

    def test_hr_expense_with_tags_01(self):
        self._test_hr_expense_with_tags_01()

    def test_hr_expense_with_tags_02(self):
        self._test_hr_expense_with_tags_02()

    def test_hr_expense_with_tags_03(self):
        self._test_hr_expense_with_tags_03()

    def test_hr_expense_without_tags(self):
        self._test_hr_expense_without_tags()


@tagged("-at_install", "post_install")
class TestHrExpenseAnalyticTagCompanyAccount(TestHrExpenseAnalyticTagBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.expense.payment_mode = "company_account"

    def test_hr_expense_with_tag(self):
        self._test_hr_expense_with_tag()

    def test_hr_expense_with_tags_01(self):
        self._test_hr_expense_with_tags_01()

    def test_hr_expense_with_tags_02(self):
        self._test_hr_expense_with_tags_02()

    def test_hr_expense_with_tags_03(self):
        self._test_hr_expense_with_tags_03()

    def test_hr_expense_without_tags(self):
        self._test_hr_expense_without_tags()
