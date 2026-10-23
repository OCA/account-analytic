# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestPurchaseBlanketOrderAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env.ref("base.res_partner_12")
        self.product_id = self.env.ref("product.product_product_9")
        self.uom_id = self.env.ref("uom.product_uom_unit")
        analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        analytic_account_manual = self.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        self.analytic_distribution_manual = {str(analytic_account_manual.id): 100}

    def test_analytic_distribution(self):
        """Create a blanket order
        Set analytic distribution on blanket order
        Check analytic distribution and line is set
        """
        bo = self.env["purchase.blanket.order"].create(
            {
                "partner_id": self.partner_id.id,
                "validity_date": datetime.today(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_uom": self.uom_id.id,
                            "original_uom_qty": 1.0,
                            "price_unit": 121.0,
                        },
                    )
                ],
            }
        )
        bo.analytic_distribution = self.analytic_distribution_manual
        bo._onchange_analytic_distribution()
        self.assertEqual(bo.analytic_distribution, self.analytic_distribution_manual)
        self.assertEqual(
            bo.line_ids.analytic_distribution, self.analytic_distribution_manual
        )

    def test_analytic_disctribution_with_new(self):
        """Create a blanket order (new)
        Set analytic distribution on blanket order
        Check analytic distribution and line is set
        """
        bo = self.env["purchase.blanket.order"].new(
            {
                "partner_id": self.partner_id.id,
                "analytic_distribution": self.analytic_distribution_manual,
                "validity_date": datetime.today(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "product_uom": self.uom_id.id,
                            "original_uom_qty": 1.0,
                            "price_unit": 121.0,
                        },
                    )
                ],
            }
        )
        bo._onchange_analytic_distribution()
        self.assertEqual(bo.analytic_distribution, self.analytic_distribution_manual)
        self.assertEqual(
            bo.line_ids.analytic_distribution, self.analytic_distribution_manual
        )
