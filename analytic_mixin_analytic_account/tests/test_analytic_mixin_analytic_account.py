# Copyright 2023 Quartile Limited
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.addons.analytic.tests.test_analytic_account import TestAnalyticAccount


class TestAnalyticMixinAnalyticAccount(TestAnalyticAccount):
    def setUp(self):
        super(TestAnalyticAccount, self).setUp()

    def test_analytic_mixin_analytic_account(self):
        distribution = self.env["account.analytic.distribution.model"].create(
            {
                "partner_id": self.partner_a.id,
                "analytic_distribution": {
                    self.analytic_account_1.id: 100,
                    self.analytic_account_2.id: 100,
                    self.analytic_account_3.id: 100,
                },
            }
        )
        distribution._compute_analytic_account_ids()
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
        distribution = self.env["account.analytic.distribution.model"].create({})
        distribution._compute_analytic_account_ids()

        self.assertFalse(distribution.analytic_account_ids)
        self.assertFalse(distribution.analytic_account_names)
