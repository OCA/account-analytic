# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common, new_test_user

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestHrTimesheetAnalyticTag(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="hr_timesheet.group_hr_timesheet_user,account_analytic_tag.group_analytic_tags,account.group_account_manager",
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Test employee",
                "user_id": cls.user.id,
            }
        )
        cls.project = cls.env["project.project"].create({"name": "Test project"})
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test task",
                "project_id": cls.project.id,
            }
        )
        aa_tag_model = cls.env["account.analytic.tag"]
        cls.analytic_tag_1 = aa_tag_model.create({"name": "Test tag 1"})
        cls.analytic_tag_2 = aa_tag_model.create({"name": "Test tag 2"})

    def _create_hr_timesheet(self):
        return (
            self.env["account.analytic.line"]
            .with_user(self.user)
            .create(
                {
                    "project_id": self.project.id,
                    "task_id": self.task.id,
                    "employee_id": self.employee.id,
                }
            )
        )

    def test_hr_timesheet_without_tags(self):
        timesheet = self._create_hr_timesheet()
        self.assertNotIn(self.analytic_tag_1, timesheet.tag_ids)
        self.assertNotIn(self.analytic_tag_2, timesheet.tag_ids)

    def test_hr_timesheet_with_tag_01(self):
        self.task.analytic_tag_ids = self.analytic_tag_1
        timesheet = self._create_hr_timesheet()
        self.assertIn(self.analytic_tag_1, timesheet.tag_ids)
        self.assertNotIn(self.analytic_tag_2, timesheet.tag_ids)

    def test_hr_timesheet_with_tag_02(self):
        self.task.analytic_tag_ids = self.analytic_tag_2
        timesheet = self._create_hr_timesheet()
        self.assertNotIn(self.analytic_tag_1, timesheet.tag_ids)
        self.assertIn(self.analytic_tag_2, timesheet.tag_ids)

    def test_hr_timesheet_with_tags(self):
        self.task.analytic_tag_ids = self.analytic_tag_1 + self.analytic_tag_2
        timesheet = self._create_hr_timesheet()
        self.assertIn(self.analytic_tag_1, timesheet.tag_ids)
        self.assertIn(self.analytic_tag_2, timesheet.tag_ids)
