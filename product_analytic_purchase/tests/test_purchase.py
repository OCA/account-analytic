# © 2015 Antiun Ingenieria - Javier Iniesta
# © 2017 Tecnativa - Luis Martínez
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPurchaseOrderLine(TransactionCase):
    def setUp(self):
        super(TestPurchaseOrderLine, self).setUp()
        self.analytic = self.env["account.analytic.account"].create(
            {
                "name": "Our Super Product Development",
            }
        )
        self.product1 = self.env["product.product"].create(
            {
                "name": "Computer SC234",
                "categ_id": self.env.ref("product.product_category_all").id,
                "list_price": 450.0,
                "standard_price": 300.0,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
                "description_sale": "17 LCD Monitor Processor AMD",
            }
        )
        self.product2 = self.env["product.product"].create(
            {
                "name": "Prepaid Consulting",
                "categ_id": self.env.ref("product.product_category_all").id,
                "list_price": 90,
                "standard_price": 40,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "description": "Example of product to invoice on order.",
                "default_code": "SERV_ORDER",
                "expense_analytic_account_id": self.analytic.id,
                "income_analytic_account_id": self.analytic.id,
            }
        )
        self.assertTrue(self.product2.expense_analytic_account_id)
        self.po = self.env["purchase.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "name": self.product1.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 12,
                            "product_uom": self.product1.uom_id.id,
                            "price_unit": 42,
                        },
                    )
                ],
            }
        )
        self.po_line1 = self.po.order_line[0]

    def test_onchange_product_id(self):
        self.po_line1.product_id = self.product2.id
        self.po_line1.onchange_product_id()
        self.assertEqual(
            self.po_line1.account_analytic_id.id,
            self.product2.expense_analytic_account_id.id,
        )

    def test_create(self):
        pol_vals = {
            "product_id": self.product2.id,
            "name": self.product2.name,
            "date_planned": "2017-07-17 12:42:12",
            "product_qty": 42,
            "product_uom": self.product2.uom_id.id,
            "price_unit": 42,
            "order_id": self.po.id,
        }
        po_line2 = self.env["purchase.order.line"].create(pol_vals)
        self.assertEqual(
            po_line2.account_analytic_id.id,
            self.product2.expense_analytic_account_id.id,
        )
