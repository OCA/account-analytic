# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAnalyticDistributionDisplay(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # A model provided by the ``analytic`` addon itself that inherits
        # ``analytic.mixin``, used here to keep this module's dependencies
        # limited to ``analytic``.
        cls.model = cls.env["account.analytic.distribution.model"]
        cls.plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        cls.account_a = cls.env["account.analytic.account"].create(
            {"name": "Obra 218", "plan_id": cls.plan.id}
        )
        cls.account_b = cls.env["account.analytic.account"].create(
            {"name": "Administrativo", "plan_id": cls.plan.id}
        )

    def test_single_account(self):
        record = self.model.create(
            {"analytic_distribution": {str(self.account_a.id): 100.0}}
        )
        self.assertEqual(
            record.analytic_distribution_display,
            "Obra 218 (100.00%)",
        )

    def test_multiple_accounts_ordering(self):
        record = self.model.create(
            {
                "analytic_distribution": {
                    str(self.account_a.id): 60.0,
                    str(self.account_b.id): 40.0,
                }
            }
        )
        self.assertEqual(
            record.analytic_distribution_display,
            "Obra 218 (60.00%) | Administrativo (40.00%)",
        )

    def test_empty_distribution(self):
        record = self.model.create({"analytic_distribution": {}})
        self.assertFalse(record.analytic_distribution_display)
        record = self.model.create({"analytic_distribution": False})
        self.assertFalse(record.analytic_distribution_display)

    def test_missing_account(self):
        missing_id = self.account_b.id
        self.account_b.unlink()
        record = self.model.create({"analytic_distribution": {str(missing_id): 100.0}})
        self.assertEqual(
            record.analytic_distribution_display,
            "ID %s (100.00%%)" % missing_id,
        )

    def test_archived_account(self):
        self.account_a.active = False
        record = self.model.create(
            {"analytic_distribution": {str(self.account_a.id): 100.0}}
        )
        self.assertEqual(
            record.analytic_distribution_display,
            "Obra 218 (100.00%)",
        )

    def test_multi_plan_key(self):
        record = self.model.create(
            {
                "analytic_distribution": {
                    "%s,%s" % (self.account_a.id, self.account_b.id): 100.0
                }
            }
        )
        self.assertEqual(
            record.analytic_distribution_display,
            "Obra 218 + Administrativo (100.00%)",
        )

    def test_no_extra_queries(self):
        # Computing the field for many records must not scale linearly with
        # the number of records (no browse/search inside a loop). Odoo
        # batches non-stored compute fields across all pending records of a
        # model, so comparing two separately created batches is unreliable;
        # instead we bound the query count for a single large batch.
        records = self.model.create(
            [
                {"analytic_distribution": {str(self.account_a.id): 100.0}}
                for _ in range(50)
            ]
        )
        records.invalidate_recordset(["analytic_distribution_display"])
        self.env.flush_all()
        self.env.cr.flush()
        count_before = self.env.cr.sql_log_count
        records.mapped("analytic_distribution_display")
        self.env.cr.flush()
        query_count = self.env.cr.sql_log_count - count_before
        self.assertLess(query_count, 10)
