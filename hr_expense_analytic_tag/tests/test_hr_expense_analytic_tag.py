# Copyright 2023-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form, tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged("-at_install", "post_install")
class TestHrExpenseAnalyticTag(TestExpenseCommon):
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

    def _action_submit_expenses(self, expense):
        res = expense.action_submit_expenses()
        sheet_form = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(sheet_form.state, "draft")
        sheet_form.action_submit_sheet()
        self.assertEqual(sheet_form.state, "submit")
        return sheet_form

    def test_hr_expense_with_tag(self):
        """Tag without analytic accounts."""
        self.expense.analytic_distribution = {self.analytic_account_1.id: 100}
        self.expense.analytic_tag_ids = self.analytic_tag_1
        expense_sheet = self._action_submit_expenses(self.expense)
        expense_sheet.action_approve_expense_sheets()
        expense_sheet.action_sheet_move_post()
        move = expense_sheet.account_move_ids
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_hr_expense_with_tags_01(self):
        """Tags without analytic accounts."""
        self.expense.analytic_distribution = {self.analytic_account_1.id: 100}
        self.expense.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        expense_sheet = self._action_submit_expenses(self.expense)
        expense_sheet.action_approve_expense_sheets()
        expense_sheet.action_sheet_move_post()
        move = expense_sheet.account_move_ids
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    def test_hr_expense_with_tags_02(self):
        """Tags with analytic account and expense analytic account 1 + 2."""
        self.analytic_tag_1.account_analytic_id = self.analytic_account_1
        self.analytic_tag_2.account_analytic_id = self.analytic_account_2
        self.expense.analytic_distribution = {
            self.analytic_account_1.id: 50,
            self.analytic_account_2.id: 50,
        }
        self.expense.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        expense_sheet = self._action_submit_expenses(self.expense)
        expense_sheet.action_approve_expense_sheets()
        expense_sheet.action_sheet_move_post()
        move = expense_sheet.account_move_ids
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertIn(self.analytic_tag_2, tags)

    def test_hr_expense_with_tags_03(self):
        """Tags with analytic account and expense analytic account 1."""
        self.analytic_tag_1.account_analytic_id = self.analytic_account_1
        self.analytic_tag_2.account_analytic_id = self.analytic_account_2
        self.expense.analytic_distribution = {
            self.analytic_account_1.id: 50,
        }
        self.expense.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        expense_sheet = self._action_submit_expenses(self.expense)
        expense_sheet.action_approve_expense_sheets()
        expense_sheet.action_sheet_move_post()
        move = expense_sheet.account_move_ids
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)

    def test_hr_expense_without_tags(self):
        self.expense.analytic_distribution = {self.analytic_account_1.id: 100}
        expense_sheet = self._action_submit_expenses(self.expense)
        expense_sheet.action_approve_expense_sheets()
        expense_sheet.action_sheet_move_post()
        move = expense_sheet.account_move_ids
        tags = move.mapped("line_ids.analytic_line_ids.tag_ids")
        self.assertNotIn(self.analytic_tag_1, tags)
        self.assertNotIn(self.analytic_tag_2, tags)
