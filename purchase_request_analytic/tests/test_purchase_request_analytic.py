# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPurchaseRequestAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Default",
            },
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Account Analytic for Tests",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {
                "name": "Account Analytic for Tests 2",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.analytic_distribution = {str(cls.analytic_account.id): 100}
        cls.analytic_distribution2 = {str(cls.analytic_account2.id): 100}

    def test_analytic_distribution(self):
        """The analytic distribution on the request is propagated to its lines"""
        product_id = self.env.ref("product.product_product_9")
        pr = self.env["purchase.request"].create(
            {
                "requested_by": self.env.user.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product_id.name,
                            "product_id": product_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                        },
                    )
                ],
            }
        )

        pr.analytic_distribution = self.analytic_distribution
        self.assertEqual(pr.analytic_distribution, self.analytic_distribution)
        self.assertEqual(pr.line_ids.analytic_distribution, self.analytic_distribution)

    def test_all_analytic_accounts(self):
        """The distribution assigned to all the lines is assigned to the request"""
        product_id = self.env.ref("product.product_product_9")
        pr = self.env["purchase.request"].create(
            {
                "requested_by": self.env.user.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product_id.name,
                            "product_id": product_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "analytic_distribution": self.analytic_distribution,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": product_id.name,
                            "product_id": product_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "analytic_distribution": self.analytic_distribution,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(pr.analytic_distribution, self.analytic_distribution)

    def test_not_all_analytic_accounts(self):
        """The distribution assigned to some lines is not assigned to the request.

        If any distribution was set on the request, it is unset.
        """
        product_id = self.env.ref("product.product_product_9")
        pr = self.env["purchase.request"].create(
            {
                "requested_by": self.env.user.id,
                "analytic_distribution": self.analytic_distribution,
            }
        )
        pr.write(
            {
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product_id.name,
                            "product_id": product_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "analytic_distribution": self.analytic_distribution,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": product_id.name,
                            "product_id": product_id.id,
                            "product_qty": 1.0,
                            "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                            "analytic_distribution": self.analytic_distribution2,
                        },
                    ),
                ],
            }
        )
        self.assertFalse(pr.analytic_distribution)
