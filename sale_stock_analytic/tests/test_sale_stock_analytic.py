# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.base.tests.common import BaseCommon


class TestSaleStockAnalytic(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.product_model = cls.env["product.product"]

        cls.product = cls.product_model.create({"name": "Product test"})
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "AA 1", "plan_id": analytic_plan.id}
        )

        cls.sale_order = cls.sale_order_model.create(
            {
                "partner_id": cls.partner.id,
            }
        )
        cls.sale_order_line = cls.sale_order_line_model.create(
            {
                "name": "sale order line test",
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "analytic_distribution": dict({str(cls.analytic_account.id): 100.0}),
            }
        )

    def test_sale_stock_analytic(self):
        self.sale_order.action_confirm()
        self.move = self.sale_order.picking_ids.move_ids
        self.assertEqual(
            self.move.analytic_distribution, self.sale_order_line.analytic_distribution
        )
