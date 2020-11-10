# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleStockAnalytic(TransactionCase):
    def setUp(self):
        super(TestSaleStockAnalytic, self).setUp()
        self.sale_order_model = self.env["sale.order"]
        self.sale_order_line_model = self.env["sale.order.line"]
        self.analytic_tag_model = self.env["account.analytic.tag"]
        self.product_model = self.env["product.product"]
        self.res_partner_model = self.env["res.partner"]

        self.analytic_tag_1 = self.analytic_tag_model.create({"name": "Tag test 1"})
        self.analytic_tag_2 = self.analytic_tag_model.create({"name": "Tag test 2"})
        self.partner = self.res_partner_model.create({"name": "Partner test"})
        self.product = self.product_model.create({"name": "Product test"})
        self.analytic_account = self.env.ref("analytic.analytic_agrolait")

        self.sale_order = self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": self.analytic_account.id,
            }
        )
        self.sale_order_line = self.sale_order_line_model.create(
            {
                "name": "sale order line test",
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag_1.id, self.analytic_tag_2.id])
                ],
            }
        )

    def test_sale_stock_analytic(self):
        self.sale_order.action_confirm()
        self.move = self.sale_order.picking_ids.move_ids_without_package
        self.assertEqual(self.move.analytic_account_id, self.analytic_account)
        self.assertEqual(
            self.move.analytic_tag_ids.ids,
            [self.analytic_tag_1.id, self.analytic_tag_2.id],
        )
