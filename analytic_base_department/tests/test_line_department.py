# Copyright 2016 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class LineDepartmentCase(TransactionCase):
    def setUp(self):
        """Assign user and department."""
        super(LineDepartmentCase, self).setUp()
        # base.user_demo --> hr.employee_qdp --> hr.dep_rd
        self.user = self.env.ref("base.user_demo")
        self.dep = self.env.ref("hr.dep_rd")

    def test_default_department(self):
        """In a new users form, a user set only the firstname."""
        aal = self.env["account.analytic.line"].with_user(self.user).new()
        department_id = aal.default_get(["department_id"]).get("department_id")
        self.assertEqual(department_id, self.dep.id)

    def test_no_employees(self):
        """Tesing lines created by users w/out employee records."""
        self.user.employee_ids = [(5, 0)]
        aal = self.env["account.analytic.line"].with_user(self.user).new()
        department_id = aal.default_get(["department_id"]).get("department_id")
        self.assertFalse(department_id)
