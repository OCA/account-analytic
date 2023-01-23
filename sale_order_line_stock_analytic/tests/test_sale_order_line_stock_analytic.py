# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.sale_order_line_analytic.tests.test_sale_order_line_analytic import (
    TestSaleOrderLineAnalytic,
)


class TestSaleOrderLineStockAnalytic(TestSaleOrderLineAnalytic):
    def setUp(self):
        super().setUp()

    def test_create_picking(self):
        sale_order = self.SaleOder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product_product.list_price,
                            "name": self.product_product.name,
                            "analytic_account_id": self.analytic_account_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_product.id,
                            "product_uom_qty": 2,
                            "price_unit": self.product_product.list_price,
                            "name": self.product_product.name,
                            "analytic_account_id": self.analytic_account_2.id,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()

        self.assertTrue(sale_order.picking_ids)
        for line in sale_order.picking_ids.move_ids_without_package:
            self.assertEqual(
                line.analytic_account_id.id, line.sale_line_id.analytic_account_id.id
            )

        wiz = self.SaleAdvancePaymentInvoice.with_context(
            active_model="sale.order",
            active_ids=[sale_order.id],
            active_id=sale_order.id,
            default_journal_id=self.sale_journal.id,
        ).create({"advance_payment_method": "delivered"})
        wiz.create_invoices()

        for line in sale_order.order_line:
            self.assertEqual(
                line.analytic_account_id.id, line.invoice_lines.analytic_account_id.id
            )
