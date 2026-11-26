# Copyright 2026 Open Source Integrators - Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestImportAnalyticColumns(AccountTestInvoicingCommon):
    """Journal items can be given an analytic distribution through the
    analytic_1_id..analytic_4_id import columns, on create and on write."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        plan = cls.env["account.analytic.plan"].create({"name": "Import Plan"})
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "Import AA 1", "plan_id": plan.id}
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "Import AA 2", "plan_id": plan.id}
        )

    def _distribution_key(self, *accounts):
        return ",".join(str(account.id) for account in accounts)

    def test_create_line_with_analytic_columns(self):
        """Creating a journal item with analytic_N_id columns stores the
        matching analytic distribution; the columns themselves are not
        persisted."""
        move = self._create_invoice()
        line = move.invoice_line_ids[0]
        vals = line.copy_data({})[0]
        vals.pop("analytic_distribution", None)
        new_line = self.env["account.move.line"].create(
            {
                **vals,
                "analytic_1_id": self.analytic_account_1.id,
                "analytic_2_id": self.analytic_account_2.id,
            }
        )
        self.assertEqual(
            new_line.analytic_distribution,
            {
                self._distribution_key(
                    self.analytic_account_1, self.analytic_account_2
                ): 100
            },
        )
        new_line.invalidate_recordset()
        self.assertFalse(new_line.analytic_1_id)
        self.assertFalse(new_line.analytic_2_id)

    def test_write_line_with_analytic_columns(self):
        """Updating a journal item through the analytic_N_id columns
        replaces its analytic distribution."""
        move = self._create_invoice()
        line = move.invoice_line_ids[0]
        line.write(
            {
                "analytic_1_id": self.analytic_account_1.id,
                "analytic_2_id": self.analytic_account_2.id,
            }
        )
        self.assertEqual(
            line.analytic_distribution,
            {
                self._distribution_key(
                    self.analytic_account_1, self.analytic_account_2
                ): 100
            },
        )
        # A write providing an explicit analytic_distribution wins over the
        # import columns.
        line.write(
            {
                "analytic_1_id": self.analytic_account_1.id,
                "analytic_distribution": {str(self.analytic_account_2.id): 100},
            }
        )
        self.assertEqual(
            line.analytic_distribution, {str(self.analytic_account_2.id): 100}
        )
