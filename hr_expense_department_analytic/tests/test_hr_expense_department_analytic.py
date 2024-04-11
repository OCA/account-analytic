# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("-at_install", "post_install")
class TestHrExpenseDepartmentAnalytic(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        private_address = cls.env["res.partner"].create({"name": "A private address"})
        work_address = cls.env["res.partner"].create({"name": "A work address"})
        cls.expense_employee = cls.env["hr.employee"].create(
            {
                "name": "expense_employee",
                "user_id": cls.env.user.id,
                "address_home_id": private_address.id,
                "address_id": work_address.id,
            }
        )

        cls.default_plan = cls.env["account.analytic.plan"].create(
            {"name": "Default", "company_id": False}
        )
        cls.analytic_account_a = cls.env["account.analytic.account"].create(
            {
                "name": "analytic_account_a",
                "company_id": False,
                "plan_id": cls.default_plan.id,
            }
        )

        cls.department = cls.env["hr.department"].create(
            {
                "name": "Test Department",
                "member_ids": [(4, cls.expense_employee.id)],
                "account_analytic_id": cls.analytic_account_a.id,
            }
        )

    def test_1(self):
        expense_sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense for John Smith",
                "employee_id": self.expense_employee.id,
                "accounting_date": "2021-01-01",
                "expense_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Car Travel Expenses",
                            "employee_id": self.expense_employee.id,
                            "total_amount": 500.00,
                        },
                    )
                ],
            }
        )

        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()

        self.assertEqual(expense_sheet.state, "post")
        move = expense_sheet.account_move_id

        line_with_expense = move.line_ids.filtered(lambda rec: rec.expense_id)

        self.assertEqual(
            line_with_expense.analytic_distribution,
            {str(self.analytic_account_a.id): 100.0},
        )
