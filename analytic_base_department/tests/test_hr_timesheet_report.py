# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TimesheetsReportDepartmentCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.department = cls.env.ref("hr.dep_rd")
        cls.plan = cls.env.ref("analytic.analytic_plan_projects")
        cls.account = cls.env["account.analytic.account"].create(
            {
                "name": "Test analytic account",
                "department_id": cls.department.id,
                "plan_id": cls.plan.id,
            }
        )
        cls.project = cls.env["project.project"].create(
            {"name": "Test project", "account_id": cls.account.id}
        )
        cls.employee = cls.env.ref("hr.employee_admin")
        cls.line = cls.env["account.analytic.line"].create(
            {
                "name": "Test timesheet line",
                "account_id": cls.account.id,
                "project_id": cls.project.id,
                "employee_id": cls.employee.id,
                "unit_amount": 1.0,
            }
        )

    def test_account_department_id_in_report(self):
        """account_department_id must be readable from the reporting view.

        Without this fix, timesheets.analysis.report doesn't expose the
        field at all, which breaks the shared search view arch as soon as
        both analytic_base_department and hr_timesheet are installed
        together.
        """
        report_line = self.env["timesheets.analysis.report"].browse(self.line.id)
        self.assertEqual(report_line.account_department_id, self.department)
