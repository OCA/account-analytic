# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestPurchaseStockAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.purchase_order_model = cls.env["purchase.order"]
        cls.purchase_order_line_model = cls.env["purchase.order.line"]
        cls.product_model = cls.env["product.product"]
        cls.res_partner_model = cls.env["res.partner"]

        cls.analytic_distribution = dict(
            {str(cls.env.ref("analytic.analytic_agrolait").id): 100.0}
        )
        cls.partner = cls.res_partner_model.create({"name": "Partner test"})
        cls.product = cls.product_model.create({"name": "Product test"})

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
                "analytic_distribution": cls.analytic_distribution,
                "date_planned": fields.Datetime.today(),
                "product_uom": cls.product.uom_po_id.id,
            }
        )

    def test_purchase_stock_analytic(self):
        self.purchase_order.button_confirm()
        self.move = self.purchase_order.picking_ids.move_ids_without_package
        self.assertEqual(self.move.analytic_distribution, self.analytic_distribution)
