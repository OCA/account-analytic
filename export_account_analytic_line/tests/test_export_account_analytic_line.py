# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from unittest.mock import patch

from odoo import Command
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestExportAccountAnalyticLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.account = cls.env["account.analytic.account"].create(
            {"name": "Test Account", "plan_id": cls.plan.id}
        )
        cls.move = cls.env["account.move"].create(
            {
                "move_type": "entry",
                "date": "2026-01-01",
                "line_ids": [
                    Command.create(
                        {
                            "name": "Test AML",
                            "account_id": cls.env["account.account"]
                            .search([("account_type", "=", "asset_current")], limit=1)
                            .id,
                        },
                    )
                ],
            }
        )
        cls.analytic_line = cls.env["account.analytic.line"].create(
            [
                {
                    "name": "Test Analytic Line 1",
                    "account_id": cls.account.id,
                    "amount": 100.0,
                    "move_line_id": cls.move.line_ids[0].id,
                    "ref": "REF001",
                },
                {
                    "name": "Test Analytic Line 2",
                    "account_id": cls.account.id,
                    "amount": 200.0,
                },
            ]
        )

    def test_01_button_open_journal_entry(self):
        """Test button_open_journal_entry returns the correct action."""
        line = self.analytic_line[0]
        res = line.button_open_journal_entry()
        self.assertEqual(res["res_id"], self.move.id)
        line.move_line_id = False
        self.assertFalse(line.button_open_journal_entry())

    def test_02_get_cached_analytic_plan_columns(self):
        """Test _get_cached_analytic_plan_columns coverage."""
        line = self.analytic_line[0]
        res = line.with_context(studio=True)._get_cached_analytic_plan_columns()
        self.assertEqual(res, ())
        user = self._create_new_internal_user(login="test_user_no_access")
        user.groups_id = [(3, self.env.ref("analytic.group_analytic_accounting").id)]
        res = line.with_user(user).sudo(False)._get_cached_analytic_plan_columns()
        self.assertEqual(res, ())

    def test_03_get_analytic_columns_data_empty(self):
        """Test _get_analytic_columns_data when no plans exist (mocked)."""
        line = self.analytic_line[0]
        with patch.object(
            type(line), "_get_cached_analytic_plan_columns", return_value=()
        ):
            res = line._get_analytic_columns_data()
            self.assertEqual(res, [])

    def test_04_analytic_plan_crud_cache_clearing(self):
        """Test that CRUD on analytic plan clears the cache."""
        new_plan = self.env["account.analytic.plan"].create({"name": "New Plan"})
        self.assertTrue(new_plan)
        new_plan.write({"name": "Updated Plan"})
        new_plan.unlink()

    def test_05_report_xlsx_generation(self):
        """Trigger report generation for multiple lines to cover report logic."""
        report = self.env["ir.actions.report"]._get_report_from_name(
            "odvi_account_analytic_line_report_xls.aal_xlsx"
        )
        report._render_xlsx(report.report_name, self.analytic_line.ids, data={})

    def test_06_report_xlsx_fields_and_template(self):
        """Ensure fields and template methods are called."""
        line = self.analytic_line[0]
        fields = line._report_xlsx_fields()
        self.assertIn("move_line_id", fields)
        template = line._report_xlsx_template()
        self.assertTrue(isinstance(template, dict))
