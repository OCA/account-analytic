# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.SavepointCase):
    """ Use case : Prepare some data for current test case """

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseProcurementAnalytic, cls).setUpClass()
        vendor = cls.env["res.partner"].create({"name": "Partner #2"})
        supplierinfo = cls.env["product.supplierinfo"].create({"name": vendor.id})
        mto = cls.env.ref("stock.route_warehouse0_mto")
        buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "seller_ids": [(6, 0, [supplierinfo.id])],
                "route_ids": [(6, 0, [buy.id, mto.id])],
            }
        )
        supplierinfo_service = cls.env["product.supplierinfo"].create(
            {"name": vendor.id}
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

    def test_sale_to_procurement(self):
        analytic_account = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account"}
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": analytic_account.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product.list_price,
                            "name": self.product.name,
                        },
                    )
                ],
                "picking_policy": "direct",
            }
        )
        sale_order.with_context(test_enabled=True).action_confirm()

        purchase_order = self.env["purchase.order.line"].search(
            [("account_analytic_id", "=", analytic_account.id)]
        )
        self.assertTrue(purchase_order)

    def test_sale_service_product(self):
        analytic_account = self.env["account.analytic.account"].create(
            {"name": "Test Service Analytic Account"}
        )
        sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": analytic_account.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_product.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product.list_price,
                            "name": self.product.name,
                        },
                    )
                ],
                "picking_policy": "direct",
            }
        )
        sale_order.with_context(test_enabled=True).action_confirm()

        purchase_order = self.env["purchase.order.line"].search(
            [("account_analytic_id", "=", analytic_account.id)]
        )
        self.assertTrue(purchase_order)
