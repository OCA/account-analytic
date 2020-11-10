# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseStockAnalytic(TransactionCase):
    def setUp(self):
        super(TestPurchaseStockAnalytic, self).setUp()
        self.purchase_order_model = self.env["purchase.order"]
        self.purchase_order_line_model = self.env["purchase.order.line"]
        self.analytic_tag_model = self.env["account.analytic.tag"]
        self.product_model = self.env["product.product"]
        self.res_partner_model = self.env["res.partner"]

        self.analytic_tag_1 = self.analytic_tag_model.create({"name": "Tag test 1"})
        self.analytic_tag_2 = self.analytic_tag_model.create({"name": "Tag test 2"})
        self.partner = self.res_partner_model.create({"name": "Partner test"})
        self.product = self.product_model.create({"name": "Product test"})
        self.analytic_account = self.env.ref("analytic.analytic_agrolait")

        self.purchase_order = self.purchase_order_model.create(
            {"partner_id": self.partner.id}
        )
        self.purchase_order_line = self.purchase_order_line_model.create(
            {
                "name": "purchase order line test",
                "product_qty": 3,
                "order_id": self.purchase_order.id,
                "price_unit": 20,
                "product_id": self.product.id,
                "account_analytic_id": self.analytic_account.id,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag_1.id, self.analytic_tag_2.id])
                ],
                "date_planned": fields.Datetime.today(),
                "product_uom": self.product.uom_po_id.id,
            }
        )

    def test_purchase_stock_analytic(self):
        self.purchase_order.button_confirm()
        self.move = self.purchase_order.picking_ids.move_ids_without_package
        self.assertEqual(self.move.analytic_account_id, self.analytic_account)
        self.assertEqual(
            self.move.analytic_tag_ids.ids,
            [self.analytic_tag_1.id, self.analytic_tag_2.id],
        )
