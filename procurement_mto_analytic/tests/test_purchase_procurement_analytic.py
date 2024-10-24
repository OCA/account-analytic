# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.TransactionCase):
    """Use case : Prepare some data for current test case"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env["res.partner"].create({"name": "Partner #2"})
        supplierinfo = cls.env["product.supplierinfo"].create(
            {"partner_id": cls.vendor.id}
        )
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
            {"partner_id": cls.vendor.id}
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
        cls.analytic_distribution = dict(
            {str(cls.env.ref("analytic.analytic_agrolait").id): 100.0}
        )

    def create_sale_order(self, product):
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "price_unit": product.list_price,
                            "name": product.name,
                            "analytic_distribution": self.analytic_distribution,
                        },
                    )
                ],
                "picking_policy": "direct",
            }
        )
        return sale_order

    def test_sale_to_procurement(self):
        sale_order = self.create_sale_order(self.product)
        sale_order.with_context(test_enabled=True).action_confirm()
        purchase_order_line = self.env["purchase.order.line"].search(
            [("partner_id", "=", self.vendor.id)]
        )
        self.assertTrue(purchase_order_line)
        self.assertEqual(
            purchase_order_line.analytic_distribution, self.analytic_distribution
        )

    def test_sale_service_product(self):
        sale_order = self.create_sale_order(self.service_product)
        sale_order.with_context(test_enabled=True).action_confirm()
        purchase_order_line = self.env["purchase.order.line"].search(
            [("partner_id", "=", self.vendor.id)]
        )
        self.assertTrue(purchase_order_line)
        self.assertTrue(
            purchase_order_line.analytic_distribution, self.analytic_distribution
        )
