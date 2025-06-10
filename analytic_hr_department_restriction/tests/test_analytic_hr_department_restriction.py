# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.tests import new_test_user
from odoo.tests.common import users

from odoo.addons.base.tests.common import BaseCommon


class TestAnalyticHrDepartmentRestriction(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                test_analytic_hr_department_restriction=True,
            )
        )
        cls.department_a = cls.env["hr.department"].create(
            {
                "name": "Test department A",
                "company_id": cls.env.company.id,
            }
        )
        cls.department_b = cls.env["hr.department"].create(
            {
                "name": "Test department B",
                "company_id": False,
            }
        )
        cls.basic_user = new_test_user(cls.env, login="test-basic_user")
        cls.env["hr.employee"].create(
            {
                "name": "Test employee Basic",
                "user_id": cls.basic_user.id,
                "department_id": cls.department_a.id,
            }
        )
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="base.group_user,analytic.group_analytic_accounting",
        )
        cls.env["hr.employee"].create(
            {
                "name": "Test employee A",
                "user_id": cls.user.id,
                "department_id": cls.department_a.id,
            }
        )
        cls.user_extra = new_test_user(
            cls.env,
            login="test-user_extra",
            groups="base.group_user,analytic_hr_department_restriction.group_analytic_accounting_without_department",  # noqa: B950
        )
        cls.env["hr.employee"].create(
            {
                "name": "Test employee A extra",
                "user_id": cls.user_extra.id,
                "department_id": cls.department_a.id,
            }
        )
        cls.manager = new_test_user(
            cls.env,
            login="test-manager",
            groups="account.group_account_invoice,analytic.group_analytic_accounting",
        )
        cls.env["hr.employee"].create(
            {
                "name": "Test employee B",
                "user_id": cls.manager.id,
                "department_id": cls.department_b.id,
            }
        )
        cls.plan_a = cls.env["account.analytic.plan"].create(
            {
                "name": "Test plan A",
                "department_ids": [Command.set(cls.department_a.ids)],
            }
        )
        cls.account_a = cls.env["account.analytic.account"].create(
            {
                "name": "Test account A",
                "plan_id": cls.plan_a.id,
                "department_ids": [Command.set(cls.department_a.ids)],
                "company_id": cls.env.company.id,
            }
        )
        cls.plan_b = cls.env["account.analytic.plan"].create(
            {
                "name": "Test plan B",
                "department_ids": [Command.set(cls.department_b.ids)],
            }
        )
        cls.account_b = cls.env["account.analytic.account"].create(
            {
                "name": "Test account B",
                "plan_id": cls.plan_b.id,
                "department_ids": [Command.set(cls.department_b.ids)],
                "company_id": cls.env.company.id,
            }
        )
        cls.plan_c = cls.env["account.analytic.plan"].create({"name": "Test plan C"})
        cls.account_c = cls.env["account.analytic.account"].create(
            {
                "name": "Test account C",
                "plan_id": cls.plan_c.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.company_extra = cls.env["res.company"].create(
            {"name": "Test company extra"}
        )
        cls.user.write({"company_ids": [Command.link(cls.company_extra.id)]})

    @users("test-basic_user")
    def test_analytic_data_basic_user(self):
        accounts = self.env["account.analytic.account"].search([])
        self.assertNotIn(self.account_a, accounts)
        self.assertNotIn(self.account_b, accounts)
        self.assertNotIn(self.account_c, accounts)

    @users("test-user")
    def test_analytic_data_user(self):
        plans = self.env["account.analytic.plan"].search([])
        self.assertIn(self.plan_a, plans)
        self.assertNotIn(self.plan_b, plans)
        self.assertNotIn(self.plan_c, plans)
        accounts = self.env["account.analytic.account"].search([])
        self.assertIn(self.account_a, accounts)
        self.assertNotIn(self.account_b, accounts)
        self.assertNotIn(self.account_c, accounts)

    @users("test-user")
    def test_analytic_data_user_multi_company(self):
        # Example of use case:
        # - User with access to several companies.
        # - Employee defined in one company
        # - Department and plan with no company defined
        # - Purchase order linked to company A (different from the user's employee).
        # - No access error should be displayed and the user should be able to see
        # the corresponding plan/analytic account even if the employee's company
        # is not selected.
        self.department_a.company_id = False
        self.plan_a.department_ids = [Command.set(self.department_a.ids)]
        self.plan_b.department_ids = [Command.set(self.department_b.ids)]
        plans = (
            self.env["account.analytic.plan"]
            .with_company(self.company_extra.id)
            .search([])
        )
        self.assertIn(self.plan_a, plans)
        self.assertNotIn(self.plan_b, plans)
        self.assertNotIn(self.plan_c, plans)
        self.account_a.company_id = False
        self.account_b.company_id = False
        self.account_c.company_id = False
        accounts = (
            self.env["account.analytic.account"]
            .with_company(self.company_extra.id)
            .search([])
        )
        self.assertIn(self.account_a, accounts)
        self.assertNotIn(self.account_b, accounts)
        self.assertNotIn(self.account_c, accounts)

    @users("test-user")
    def test_get_relevant_plans(self):
        self.plan_a.department_ids = False
        items = self.env["account.analytic.plan"].get_relevant_plans(
            business_domain="general"
        )
        plan_ids = [item["id"] for item in items]
        self.assertNotIn(self.plan_a.id, plan_ids)
        self.assertNotIn(self.plan_b.id, plan_ids)
        self.assertNotIn(self.plan_c.id, plan_ids)

    @users("test-user_extra")
    def test_analytic_data_user_extra(self):
        plans = self.env["account.analytic.plan"].search([])
        self.assertIn(self.plan_a, plans)
        self.assertNotIn(self.plan_b, plans)
        self.assertIn(self.plan_c, plans)
        accounts = self.env["account.analytic.account"].search([])
        self.assertIn(self.account_a, accounts)
        self.assertNotIn(self.account_b, accounts)
        self.assertIn(self.account_c, accounts)

    @users("test-manager")
    def test_analytic_data_manager(self):
        plans = self.env["account.analytic.plan"].search([])
        self.assertIn(self.plan_a, plans)
        self.assertIn(self.plan_b, plans)
        self.assertIn(self.plan_c, plans)
        accounts = self.env["account.analytic.account"].search([])
        self.assertIn(self.account_a, accounts)
        self.assertIn(self.account_b, accounts)
        self.assertIn(self.account_c, accounts)
