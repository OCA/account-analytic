# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestSaleStockAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.product_model = cls.env["product.product"]
        cls.res_partner_model = cls.env["res.partner"]

        cls.partner = cls.res_partner_model.create({"name": "Partner test"})
        cls.product = cls.product_model.create({"name": "Product test"})
        cls.analytic_distribution = dict(
            {str(cls.env.ref("analytic.analytic_agrolait").id): 100.0}
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
                "analytic_distribution": cls.analytic_distribution,
            }
        )

    def test_sale_stock_analytic(self):
        self.sale_order.action_confirm()
        self.move = self.sale_order.picking_ids.move_ids_without_package
        self.assertEqual(self.move.analytic_distribution, self.analytic_distribution)
