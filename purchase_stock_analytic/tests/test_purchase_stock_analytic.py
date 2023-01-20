# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseStockAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.purchase_order_line_model = cls.env["purchase.order.line"]
        cls.analytic_tag_model = cls.env["account.analytic.tag"]
        cls.product_model = cls.env["product.product"]
        cls.res_partner_model = cls.env["res.partner"]

        cls.analytic_tag_1 = cls.analytic_tag_model.create({"name": "Tag test 1"})
        cls.analytic_tag_2 = cls.analytic_tag_model.create({"name": "Tag test 2"})
        cls.partner = cls.res_partner_model.create({"name": "Partner test"})
        cls.product = cls.product_model.create({"name": "Product test"})
        cls.analytic_account = cls.env.ref("analytic.analytic_agrolait")

        cls.purchase_order = cls.purchase_order_model.create(
            {"partner_id": cls.partner.id}
        )
        cls.purchase_order_line = cls.purchase_order_line_model.create(
            {
                "name": "purchase order line test",
                "product_qty": 3,
                "order_id": cls.purchase_order.id,
                "price_unit": 20,
                "product_id": cls.product.id,
                "account_analytic_id": cls.analytic_account.id,
                "analytic_tag_ids": [
                    (6, 0, [cls.analytic_tag_1.id, cls.analytic_tag_2.id])
                ],
                "date_planned": fields.Datetime.today(),
                "product_uom": cls.product.uom_po_id.id,
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
