from odoo.tests.common import TransactionCase


class TestSaleOrderLineAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        # 1) Create an analytical account
        self.analytic = self.env["account.analytic.account"].create(
            {"name": "Projecte Venda"}
        )
        # 2) Create two products:
        #    - a consumable without analytic
        self.product1 = self.env["product.product"].create(
            {
                "name": "Prod Sense Analytic",
                "categ_id": self.env.ref("product.product_category_all").id,
                "type": "consu",
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "uom_po_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        #    - a service with analytic account
        self.product2 = self.env["product.product"].create(
            {
                "name": "Servei Analytic",
                "categ_id": self.env.ref("product.product_category_all").id,
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "expense_analytic_account_id": self.analytic.id,
                "income_analytic_account_id": self.analytic.id,
            }
        )
        # 3) Create a sale order with one line using product1
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        self.so_line1 = self.so.order_line[0]

    def test_onchange_product_id(self):
        # Changing to product2 should set account_analytic_id
        self.so_line1.product_id = self.product2.id
        self.so_line1.onchange_product_id()
        self.assertEqual(
            self.so_line1.account_analytic_id.id,
            self.product2.expense_analytic_account_id.id,
        )

    def test_create(self):
        # Creating a line via create() without manual account_analytic_id
        vals = {
            "order_id": self.so.id,
            "product_id": self.product2.id,
            "product_uom_qty": 2,
            "price_unit": 20,
        }
        so_line2 = self.env["sale.order.line"].create(vals)
        self.assertEqual(
            so_line2.account_analytic_id.id,
            self.product2.expense_analytic_account_id.id,
        )
