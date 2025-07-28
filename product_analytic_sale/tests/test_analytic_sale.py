# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleOrderLineAnalyticDistribution(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderLineAnalyticDistribution, cls).setUpClass()
        # Create analytic accounts
        cls.analytic_account1 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Income"}
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Expense"}
        )
        # Distribution model
        cls.dist_model = cls.env["account.analytic.distribution"]
        # Unit of measure
        unit = cls.env.ref("uom.product_uom_unit")
        # Products for testing
        cls.product_with_income = cls.env["product.product"].create(
            {
                "name": "Product with Income",
                "list_price": 100.0,
                "standard_price": 50.0,
                "uom_id": unit.id,
                "uom_po_id": unit.id,
                "income_analytic_account_id": cls.analytic_account1.id,
            }
        )
        cls.product_no_accounts = cls.env["product.product"].create(
            {
                "name": "Product with No Analytic",
                "list_price": 100.0,
                "standard_price": 50.0,
                "uom_id": unit.id,
                "uom_po_id": unit.id,
            }
        )
        cls.product_only_expense = cls.env["product.product"].create(
            {
                "name": "Product with Only Expense",
                "list_price": 100.0,
                "standard_price": 50.0,
                "uom_id": unit.id,
                "uom_po_id": unit.id,
                "expense_analytic_account_id": cls.analytic_account2.id,
            }
        )
        # Partner
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def _create_order_line(self, product):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        return order.order_line[0]

    def test_no_product(self):
        # Create an order line without product
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        order.order_line = [(0, 0, {"product_uom_qty": 1.0, "price_unit": 10.0})]
        # Since product_id is empty, distribution should be False
        self.assertFalse(order.order_line.analytic_distribution)

    def test_income_account_distribution(self):
        """If product has income account, distribution is created or reused"""
        line = self._create_order_line(self.product_with_income)
        # First call: distribution record should be created
        dist1 = line.analytic_distribution
        self.assertTrue(dist1 and dist1._name == "account.analytic.distribution")
        self.assertEqual(dist1.account_id.id, self.analytic_account1.id)
        self.assertEqual(dist1.percent, 100)
        self.assertEqual(dist1.name, self.analytic_account1.name)
        # Second call: same record should be reused (not duplicated)
        line2 = self._create_order_line(self.product_with_income)
        dist2 = line2.analytic_distribution
        self.assertEqual(dist2.id, dist1.id)

    def test_no_analytic_accounts(self):
        """Products without income analytic yield no distribution"""
        line = self._create_order_line(self.product_no_accounts)
        self.assertFalse(line.analytic_distribution)

    def test_only_expense_account(self):
        """Products with only expense analytic yield no distribution"""
        line = self._create_order_line(self.product_only_expense)
        self.assertFalse(line.analytic_distribution)
