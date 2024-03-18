# © 2015 Antiun Ingenieria - Javier Iniesta
# © 2017 Tecnativa - Luis Martínez
# © 2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPurchaseOrderLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.default_plan = cls.env["account.analytic.plan"].create(
            {"name": "Default Plan", "company_id": False}
        )
        cls.analytic = cls.env["account.analytic.account"].create(
            {
                "name": "Our Super Product Development",
                "plan_id": cls.default_plan.id,
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Computer SC234",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 450.0,
                "standard_price": 300.0,
                "type": "consu",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "description_sale": "17 LCD Monitor Processor AMD",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Prepaid Consulting",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 90,
                "standard_price": 40,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
                "description": "Example of product to invoice on order.",
                "default_code": "SERV_ORDER",
                "expense_analytic_account_id": cls.analytic.id,
                "income_analytic_account_id": cls.analytic.id,
            }
        )
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "name": cls.product1.name,
                            "date_planned": "2017-07-17 12:42:12",
                            "product_qty": 12,
                            "product_uom": cls.product1.uom_id.id,
                            "price_unit": 42,
                        },
                    )
                ],
            }
        )
        cls.po_line1 = cls.po.order_line[0]

    def test_change_product_id(self):
        self.po_line1.product_id = self.product2.id
        analytic_account_id = [key for key in self.po_line1.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
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
        analytic_account_id = [key for key in po_line2.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.product2.expense_analytic_account_id.id,
        )
