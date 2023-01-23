# Copyright 2023 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrderLineAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.AccountAnalyticAccount = self.env["account.analytic.account"]
        self.ProductProduct = self.env["product.product"]
        self.SaleOder = self.env["sale.order"]
        self.SaleAdvancePaymentInvoice = self.env["sale.advance.payment.inv"]

        self.sale_journal = self.env["account.journal"].search(
            [("company_id", "=", self.env.company.id), ("type", "=", "sale")], limit=1
        )
        self.partner = self.env.ref("base.res_partner_12")
        self.product_service = self.ProductProduct.create(
            {"name": "Service Test", "type": "service"}
        )
        self.product_product = self.ProductProduct.create(
            {"name": "Product Test", "type": "product"}
        )
        self.analytic_account_1 = self.AccountAnalyticAccount.create(
            {"name": "Analytic Account Test 1"}
        )
        self.analytic_account_2 = self.AccountAnalyticAccount.create(
            {"name": "Analytic Account Test 2"}
        )

    def test_create_sale_order(self):
        sale_order = self.SaleOder.create(
            {
                "partner_id": self.partner.id,
                "analytic_account_id": self.analytic_account_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product_service.list_price,
                            "name": self.product_service.name,
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            sale_order.order_line.analytic_account_id.id, self.analytic_account_1.id
        )

    def test_create_invoice(self):
        sale_order = self.SaleOder.create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "product_uom_qty": 1,
                            "price_unit": self.product_service.list_price,
                            "name": self.product_service.name,
                            "analytic_account_id": self.analytic_account_1.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_service.id,
                            "product_uom_qty": 2,
                            "price_unit": self.product_service.list_price,
                            "name": self.product_service.name,
                            "analytic_account_id": self.analytic_account_2.id,
                        },
                    ),
                ],
            }
        )
        sale_order.action_confirm()
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
