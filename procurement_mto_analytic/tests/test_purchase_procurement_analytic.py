# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestPurchaseProcurementAnalytic(common.TransactionCase):
    """Use case : Prepare some data for current test case"""

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseProcurementAnalytic, cls).setUpClass()
        vendor = cls.env["res.partner"].create({"name": "Partner #2"})
        supplierinfo = cls.env["product.supplierinfo"].create({"name": vendor.id})
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
        analytic_account_2 = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account 2"}
        )
        analytic_account_3 = self.env["account.analytic.account"].create(
            {"name": "Test Analytic Account 3"}
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
        sale_order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": analytic_account_3.id,
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
        # No purchase order lines should initially be found with newly
        # created analytic account.
        purchase_order = self.env["purchase.order.line"].search(
            [("account_analytic_id", "=", analytic_account.id)]
        )
        self.assertFalse(purchase_order)
        # One purchase order line should be found with newly created
        # analytic account after confirming sale order.
        sale_order.with_context(test_enabled=True).action_confirm()

        purchase_order = self.env["purchase.order.line"].search(
            [("account_analytic_id", "=", analytic_account.id)]
        )
        self.assertEqual(len(purchase_order.order_id.order_line), 1)
        # Adding a new sale order line should merge a new purchase order line
        # into the existing purchase order line, as the analytic accounts
        # match. As a result, just one purchase order line should still be
        # found.
        self.env["sale.order.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": self.product.list_price,
                "name": self.product.name,
                "order_id": sale_order.id,
            }
        )
        self.assertEqual(len(purchase_order.order_id.order_line), 1)
        # Changing the analytic account on the purchase order line and then
        # adding a new line to the sale order should create a new purchase
        # order line, as the analytic accounts no longer match.
        purchase_order.order_id.order_line[
            0
        ].account_analytic_id = analytic_account_2.id
        self.env["sale.order.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": self.product.list_price,
                "name": self.product.name,
                "order_id": sale_order.id,
            }
        )
        self.assertEqual(len(purchase_order.order_id.order_line), 2)
        # If no analytic accounts are set, purchase order lines should
        # get merged.
        po_linecount = len(self.env["purchase.order.line"].search([]))
        sale_order2.with_context(test_enabled=True).action_confirm()
        purchase_order = self.env["purchase.order.line"].search(
            [("account_analytic_id", "=", analytic_account_3.id)]
        )
        purchase_order.order_id.order_line[0].account_analytic_id = []
        self.env["sale.order.line"].create(
            {
                "product_id": self.product.id,
                "product_uom_qty": 1,
                "price_unit": self.product.list_price,
                "name": self.product.name,
                "order_id": sale_order.id,
            }
        )
        self.assertEqual(
            len(self.env["purchase.order.line"].search([])), po_linecount + 1
        )

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
