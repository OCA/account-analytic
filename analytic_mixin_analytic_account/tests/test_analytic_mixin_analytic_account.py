# Copyright 2023 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests import TransactionCase


class TestAnalyticMixinAnalyticAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.analytic_plan_1 = cls.env["account.analytic.plan"].create(
            {"name": "Plan 1"}
        )
        cls.analytic_plan_2 = cls.env["account.analytic.plan"].create(
            {"name": "Plan 2"}
        )
        cls.analytic_plan_3 = cls.env["account.analytic.plan"].create(
            {"name": "Plan 3"}
        )
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "Account 1", "plan_id": cls.analytic_plan_1.id}
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "Account 2", "plan_id": cls.analytic_plan_2.id}
        )
        cls.analytic_account_3 = cls.env["account.analytic.account"].create(
            {"name": "Account 3", "plan_id": cls.analytic_plan_3.id}
        )

    def test_analytic_mixin_analytic_account(self):
        distribution = self.env["account.analytic.distribution.model"].create(
            {
                "partner_id": self.partner.id,
                "analytic_distribution": {
                    self.analytic_account_1.id: 100,
                    self.analytic_account_2.id: 100,
                    self.analytic_account_3.id: 100,
                },
            }
        )
        self.assertEqual(
            set(distribution.analytic_account_ids.ids),
            {
                self.analytic_account_1.id,
                self.analytic_account_2.id,
                self.analytic_account_3.id,
            },
        )
        self.assertIn(self.analytic_account_1.name, distribution.analytic_account_names)
        self.assertIn(self.analytic_account_2.name, distribution.analytic_account_names)
        self.assertIn(self.analytic_account_3.name, distribution.analytic_account_names)

        # Test analytic_account_ids empty
        distribution = self.env["account.analytic.distribution.model"].create(
            {"partner_id": self.partner.id}
        )
        self.assertFalse(distribution.analytic_account_ids)
        self.assertFalse(distribution.analytic_account_names)

    def test_analytic_distribution_with_deleted_account(self):
        """analytic_distribution is a JSON field, not protected by a foreign
        key: it may reference deleted analytic accounts. The compute must
        ignore them instead of raising an IntegrityError on the m2m table."""
        deleted_account = self.env["account.analytic.account"].create(
            {"name": "Deleted Account", "plan_id": self.analytic_plan_1.id}
        )
        deleted_account_id = deleted_account.id
        distribution = self.env["account.analytic.distribution.model"].create(
            {
                "partner_id": self.partner.id,
                "analytic_distribution": {
                    self.analytic_account_1.id: 50,
                    deleted_account_id: 50,
                },
            }
        )
        deleted_account.unlink()
        # Trigger the recompute with the dangling id still in the distribution
        distribution.analytic_distribution = {
            self.analytic_account_1.id: 50,
            self.analytic_account_2.id: 25,
            deleted_account_id: 25,
        }
        # Force the m2m INSERT in database, where the foreign key is checked
        distribution.flush_recordset()
        self.assertEqual(
            distribution.analytic_account_ids,
            self.analytic_account_1 | self.analytic_account_2,
        )
