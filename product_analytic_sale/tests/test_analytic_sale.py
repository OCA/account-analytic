# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import first

from odoo.addons.base.tests.common import BaseCommon


class TestSaleAnalytic(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_plan = cls.env["account.analytic.plan"].create(
            {"name": "Default Plan", "company_id": False}
        )
        cls.advance_obj = cls.env["sale.advance.payment.inv"]
        cls.analytic = cls.env["account.analytic.account"].create(
            {
                "name": "Our Super Product Development",
                "plan_id": cls.default_plan.id,
            }
        )
        cls.analytic_2 = cls.env["account.analytic.account"].create(
            {
                "name": "Our Super Product Development Bis",
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
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "name": cls.product1.name,
                            "product_uom_qty": 12,
                            "product_uom": cls.product1.uom_id.id,
                            "price_unit": 42,
                        },
                    )
                ],
            }
        )
        cls.so_line1 = first(cls.so.order_line)

    @classmethod
    def _create_down_payment_product(cls):
        wizard = cls.advance_obj.with_context(active_ids=cls.so.ids).create({})
        product = cls.env["product.product"].create(
            wizard._prepare_down_payment_product_values()
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "sale.default_deposit_product_id", product.id
        )
        cls.deposit = cls.env["product.product"].browse(
            int(
                cls.env["ir.config_parameter"].get_param(
                    "sale.default_deposit_product_id"
                )
            )
        )
        cls.deposit.income_analytic_account_id = cls.analytic

    def test_change_product_id(self):
        self.so_line1.product_id = self.product2.id
        analytic_account_id = [key for key in self.so_line1.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.product2.expense_analytic_account_id.id,
        )

    def test_create_invoice_after(self):
        """
        Create a sale order with no distribution on product 1
        Then, set a distribution
        Create the invoice and check the invoice line has the analytic
        """
        self.so.action_confirm()
        self.product1.income_analytic_account_id = self.analytic
        invoice = self.so._create_invoices()
        analytic_account_id = [
            key for key in invoice.invoice_line_ids.analytic_distribution
        ]
        self.assertEqual(int(analytic_account_id[0]), self.analytic.id)

    def test_create_invoice_distribution_plan(self):
        """
        Check the distribution plan is still well applied if no
        income_analytic_account_id field is field in
        """
        self.env["account.analytic.distribution.model"].create(
            {
                "product_id": self.product1.id,
                "analytic_distribution": {self.analytic_2.id: 100.0},
            }
        )
        self.so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "name": self.product1.name,
                            "product_uom_qty": 12,
                            "product_uom": self.product1.uom_id.id,
                            "price_unit": 42,
                        },
                    )
                ],
            }
        )
        self.so.action_confirm()
        invoice = self.so._create_invoices()
        analytic_account_id = [
            key for key in invoice.invoice_line_ids.analytic_distribution
        ]
        self.assertEqual(int(analytic_account_id[0]), self.analytic_2.id)

    def test_create(self):
        pol_vals = {
            "product_id": self.product2.id,
            "name": self.product2.name,
            "product_uom_qty": 42,
            "product_uom": self.product2.uom_id.id,
            "price_unit": 42,
            "order_id": self.so.id,
        }
        so_line2 = self.env["sale.order.line"].create(pol_vals)
        analytic_account_id = [key for key in so_line2.analytic_distribution]
        self.assertEqual(
            int(analytic_account_id[0]),
            self.product2.expense_analytic_account_id.id,
        )

    def test_advance(self):
        """
        Test advance payment on product
        """
        self.so_line1.product_id = self.product2
        self.so.action_confirm()
        wizard = self.advance_obj.with_context(active_ids=self.so.ids).create({})

        wizard.advance_payment_method = "delivered"
        invoice = wizard._create_invoices(self.so)
        self.assertTrue(invoice)
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution,
            {str(self.analytic.id): 100.0},
        )

    def test_advance_fixed(self):
        """
        Test the analytic account on down payment product
        """
        self.so.action_confirm()
        self._create_down_payment_product()
        wizard = self.advance_obj.with_context(active_ids=self.so.ids).create({})

        wizard.update(
            {
                "fixed_amount": 50.0,
                "advance_payment_method": "fixed",
            }
        )
        invoice = wizard._create_invoices(self.so)
        self.assertTrue(invoice)
        self.assertEqual(
            invoice.invoice_line_ids.analytic_distribution,
            {str(self.analytic.id): 100.0},
        )

    def test_advance_fixed_no_analytic(self):
        """
        Test that analytic account on down payment product is not set
        """
        self.so.action_confirm()
        wizard = self.advance_obj.with_context(active_ids=self.so.ids).create({})

        wizard.update(
            {
                "fixed_amount": 50.0,
                "advance_payment_method": "fixed",
            }
        )
        invoice = wizard._create_invoices(self.so)
        self.assertTrue(invoice)
        self.assertFalse(invoice.invoice_line_ids.analytic_distribution)
