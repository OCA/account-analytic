# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSaleAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleAnalytic, cls).setUpClass()
        # Create analytic accounts
        cls.analytic_account1 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic 1"}
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic 2"}
        )
        # Get unit of measure
        unit = cls.env.ref("uom.product_uom_unit")
        # Products for testing
        cls.product_with_income = cls.env["product.product"].create(
            {
                "name": "Product with Income Analytic",
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
                "name": "Product with Only Expense Analytic",
                "list_price": 100.0,
                "standard_price": 50.0,
                "uom_id": unit.id,
                "uom_po_id": unit.id,
                "expense_analytic_account_id": cls.analytic_account2.id,
            }
        )
        # Create a partner for the sale orders
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def _create_order_line(self, product):
        """Helper to create a sale order with one line for the given product."""
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

    def test_income_account_distribution(self):
        """
        If the product has an income analytic account, the distribution
        should allocate 100% to that account.
        """
        line = self._create_order_line(self.product_with_income)
        expected = {self.analytic_account1.id: 100}
        self.assertDictEqual(line.analytic_distribution, expected)

    def test_no_analytic_accounts(self):
        """
        If the product has no analytic accounts, the distribution
        should be empty.
        """
        line = self._create_order_line(self.product_no_accounts)
        self.assertEqual(line.analytic_distribution, {})

    def test_only_expense_account(self):
        """
        If the product has only an expense analytic account, the distribution
        should still be empty (no income account).
        """
        line = self._create_order_line(self.product_only_expense)
        self.assertEqual(line.analytic_distribution, {})
