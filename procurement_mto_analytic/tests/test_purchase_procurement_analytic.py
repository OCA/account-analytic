# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.TransactionCase):
    """Use case : Prepare some data for current test case"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vendor = cls.env["res.partner"].create({"name": "Partner #2"})
        supplierinfo = cls.env["product.supplierinfo"].create({"partner_id": vendor.id})
        mto = cls.env.ref("stock.route_warehouse0_mto")
        mto.write({"active": True})
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "seller_ids": [(6, 0, [supplierinfo.id])],
                "route_ids": [(6, 0, [buy.id, mto.id])],
            }
        )
        supplierinfo_service = cls.env["product.supplierinfo"].create(
            {"partner_id": vendor.id}
        )
        cls.service_product = cls.env["product.product"].create(
            {
                "name": "Product Service Test",
                "seller_ids": [(6, 0, [supplierinfo_service.id])],
                "type": "service",
                "service_to_purchase": True,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner #1"})

    def _make_analytic_account(self, name):
        return self.env["account.analytic.account"].create(
            {
                "name": name,
                "plan_id": self.env.ref("analytic.analytic_plan_projects").id,
            }
        )

    def _make_sale_physical_with_distributions(self, distributions: list[dict]):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product.list_price,
                            "name": self.product.name,
                            "analytic_distribution": distribution,
                        }
                    )
                    for distribution in distributions
                ],
                "picking_policy": "direct",
            }
        )

    def test_sale_to_procurement(self):
        analytic_account = self._make_analytic_account("Test Analytic Account")
        sale_order = self._make_sale_physical_with_distributions(
            [{str(analytic_account.id): 100}]
        )
        sale_order.action_confirm()

        purchase_line = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account.name)]
        )
        self.assertTrue(purchase_line)
        self.assertEqual(
            purchase_line.analytic_distribution, {str(analytic_account.id): 100}
        )

    def test_sale_to_procurement_different_accounts_dont_mix(self):
        analytic_account_1 = self._make_analytic_account("Test Analytic Account 1")
        analytic_account_2 = self._make_analytic_account("Test Analytic Account 2")
        sale_order = self._make_sale_physical_with_distributions(
            [
                {str(analytic_account_1.id): 100},
                {str(analytic_account_2.id): 100},
            ]
        )
        sale_order.action_confirm()

        purchase_line_1 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_1.name)]
        )
        purchase_line_2 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_2.name)]
        )
        self.assertTrue(purchase_line_1)
        self.assertTrue(purchase_line_2)
        self.assertNotEqual(
            purchase_line_1,
            purchase_line_2,
            msg="Different distributions should not be merged to the same PO line in procurement",
        )
        self.assertNotEqual(
            purchase_line_1.order_id,
            purchase_line_2.order_id,
            msg="Different distribution sets should not be merged to the same purchase order in procurement",
        )

    def test_sale_to_procurement_subsets_do_mix(self):
        analytic_account_1 = self._make_analytic_account("Test Analytic Account 1")
        analytic_account_2 = self._make_analytic_account("Test Analytic Account 2")
        analytic_account_3 = self._make_analytic_account("Test Analytic Account 3")
        sale_order = self._make_sale_physical_with_distributions(
            [
                {
                    str(analytic_account_1.id): 100,
                    str(analytic_account_2.id): 100,
                    str(analytic_account_3.id): 100,
                },
                {str(analytic_account_2.id): 100, str(analytic_account_3.id): 100},
            ]
        )
        sale_order.action_confirm()

        purchase_line_1 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_1.name)]
        )
        purchase_line_2 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_2.name)]
        )
        self.assertTrue(purchase_line_1)
        self.assertTrue(purchase_line_2)
        self.assertNotEqual(
            purchase_line_1,
            purchase_line_2,
            msg="Different distributions should not be merged to the same PO line in procurement",
        )
        self.assertEqual(
            purchase_line_1.order_id,
            purchase_line_2.order_id,
            msg="Procurements whose distributions are subsets of existing ones should go on the same PO",
        )

    def test_different_sales_with_same_analytics_do_mix(self):
        analytic_account_1 = self._make_analytic_account("Test Analytic Account 1")
        analytic_account_2 = self._make_analytic_account("Test Analytic Account 2")
        sale_order = self._make_sale_physical_with_distributions(
            [
                {str(analytic_account_1.id): 100},
                {str(analytic_account_2.id): 100},
            ]
        )
        sale_order.action_confirm()
        sale_line_1, sale_line_2 = sale_order.order_line

        purchase_line_1 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_1.name)]
        )
        purchase_line_2 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_2.name)]
        )
        self.assertTrue(purchase_line_1)
        self.assertTrue(purchase_line_2)
        self.assertNotEqual(
            purchase_line_1,
            purchase_line_2,
            msg="Different distributions should not be merged to the same PO line in procurement",
        )
        self.assertAlmostEqual(purchase_line_1.product_qty, sale_line_1.product_uom_qty)
        self.assertAlmostEqual(purchase_line_2.product_qty, sale_line_2.product_uom_qty)

        sale_order_2 = self._make_sale_physical_with_distributions(
            [
                {str(analytic_account_1.id): 100},
                {str(analytic_account_2.id): 100},
            ]
        )
        sale_order_2.action_confirm()
        second_sale_line_1, second_sale_line_2 = sale_order_2.order_line
        merged_purchase_line_1 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_1.name)]
        )
        merged_purchase_line_2 = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account_2.name)]
        )
        self.assertEqual(
            merged_purchase_line_1,
            purchase_line_1,
            msg="If a second sale is sold with the same analytics, it should "
            "by default be merged with an existing line with the same "
            "analytics",
        )
        self.assertEqual(
            merged_purchase_line_2,
            purchase_line_2,
            msg="If a second sale is sold with the same analytics, it should "
            "by default be merged with an existing line with the same "
            "analytics",
        )
        self.assertAlmostEqual(
            merged_purchase_line_1.product_qty,
            sale_line_1.product_uom_qty + second_sale_line_1.product_uom_qty,
        )
        self.assertAlmostEqual(
            merged_purchase_line_2.product_qty,
            sale_line_2.product_uom_qty + second_sale_line_2.product_uom_qty,
        )

    def test_sale_service_product(self):
        analytic_account = self._make_analytic_account("Test Service Analytic Account")
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.service_product.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product.list_price,
                            "name": self.product.name,
                            "analytic_distribution": {str(analytic_account.id): 100},
                        }
                    )
                ],
                "picking_policy": "direct",
            }
        )
        sale_order.action_confirm()

        purchase_line = self.env["purchase.order.line"].search(
            [("analytic_distribution", "=", analytic_account.name)]
        )
        self.assertTrue(purchase_line)
        self.assertEqual(
            purchase_line.analytic_distribution, {str(analytic_account.id): 100}
        )
