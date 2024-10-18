# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.base.tests.common import BaseCommon


class DistributionManualCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        AnalyticAccount = cls.env["account.analytic.account"]
        AnalyticPlan = cls.env["account.analytic.plan"]
        cls.ManualDistribution = cls.env["account.analytic.distribution.manual"]
        cls.plan_a = AnalyticPlan.create({"name": "Plan A"})
        cls.analytic_account_a1 = AnalyticAccount.create(
            {
                "name": "analytic_account_a1",
                "plan_id": cls.plan_a.id,
            }
        )
        cls.analytic_account_a2 = AnalyticAccount.create(
            {
                "name": "analytic_account_a2",
                "plan_id": cls.plan_a.id,
            }
        )
        cls.distribution_1 = cls.ManualDistribution.create(
            {
                "name": "Manual Distribution 1",
                "analytic_distribution": {
                    cls.analytic_account_a1.id: 40,
                    cls.analytic_account_a2.id: 60,
                },
            }
        )
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "product_a",
                "lst_price": 100.0,
                "standard_price": 80.0,
                "taxes_id": False,
            }
        )
        cls.partner_a = cls.env["res.partner"].create({"name": "partner_a"})
