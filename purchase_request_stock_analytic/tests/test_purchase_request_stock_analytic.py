# Copyright 2026 Scalizer (https://www.scalizer.fr)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseRequestStockAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")
        cls.route_buy.product_selectable = True
        cls.supplier = cls.env["res.partner"].create({"name": "Supplier"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Component",
                "is_storable": True,
                "purchase_request": True,
                "route_ids": [(4, cls.route_buy.id)],
                "seller_ids": [(0, 0, {"partner_id": cls.supplier.id, "price": 10.0})],
            }
        )
        plan = cls.env["account.analytic.plan"].create({"name": "Project"})
        Account = cls.env["account.analytic.account"]
        cls.distribution_a = {
            str(Account.create({"name": "Project A", "plan_id": plan.id}).id): 100.0
        }
        cls.distribution_b = {
            str(Account.create({"name": "Project B", "plan_id": plan.id}).id): 100.0
        }

    def _create_need(self, analytic_distribution=False):
        move = self.env["stock.move"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "procure_method": "make_to_order",
                "product_id": self.product.id,
                "uom_id": self.product.uom_id.id,
                "product_uom_qty": 5,
                "route_ids": [(4, self.route_buy.id)],
                "analytic_distribution": analytic_distribution,
            }
        )
        move._action_confirm()
        return move

    def _request_lines(self):
        return self.env["purchase.request.line"].search(
            [("product_id", "=", self.product.id)]
        )

    def test_need_with_analytic(self):
        """The request line and the purchase order line keep the need analytic."""
        self._create_need(self.distribution_a)
        line = self._request_lines()
        self.assertEqual(line.analytic_distribution, self.distribution_a)

        line.request_id.button_to_approve()
        line.request_id.button_approved()
        wizard = (
            self.env["purchase.request.line.make.purchase.order"]
            .with_context(
                active_model="purchase.request.line",
                active_ids=line.ids,
                active_id=line.id,
            )
            .create({"supplier_id": self.supplier.id})
        )
        wizard.make_purchase_order()
        self.assertEqual(line.purchase_lines.analytic_distribution, self.distribution_a)

    def test_needs_with_different_analytics(self):
        """Two needs with different analytics give two lines, one for each."""
        self._create_need(self.distribution_a)
        self._create_need(self.distribution_b)
        lines = self._request_lines()
        self.assertEqual(len(lines), 2)
        self.assertCountEqual(
            lines.mapped("analytic_distribution"),
            [self.distribution_a, self.distribution_b],
        )

    def test_need_without_analytic(self):
        """A need without analytic gives a line without analytic."""
        self._create_need()
        self.assertFalse(self._request_lines().analytic_distribution)
