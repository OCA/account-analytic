# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleStockAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.analytic_tag_model = cls.env["account.analytic.tag"]
        cls.product_model = cls.env["product.product"]
        cls.res_partner_model = cls.env["res.partner"]

        cls.analytic_tag_1 = cls.analytic_tag_model.create({"name": "Tag test 1"})
        cls.analytic_tag_2 = cls.analytic_tag_model.create({"name": "Tag test 2"})
        cls.partner = cls.res_partner_model.create({"name": "Partner test"})
        cls.product = cls.product_model.create({"name": "Product test"})
        cls.analytic_account = cls.env.ref("analytic.analytic_agrolait")

        cls.sale_order = cls.sale_order_model.create(
            {
                "partner_id": cls.partner.id,
                "analytic_account_id": cls.analytic_account.id,
            }
        )
        cls.sale_order_line = cls.sale_order_line_model.create(
            {
                "name": "sale order line test",
                "order_id": cls.sale_order.id,
                "product_id": cls.product.id,
                "analytic_tag_ids": [
                    (6, 0, [cls.analytic_tag_1.id, cls.analytic_tag_2.id])
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
