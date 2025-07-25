# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestSaleAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create two analytic accounts
        cls.ana_inc = cls.env["account.analytic.account"].create(
            {"name": "Income Analytic"}
        )
        cls.ana_exp = cls.env["account.analytic.account"].create(
            {"name": "Expense Analytic"}
        )
        # Product without analytic accounts
        cls.product_no_ana = cls.env["product.product"].create(
            {
                "name": "NoAnalytic",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 10,
                "standard_price": 5,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        # Product with income and expense analytic accounts
        cls.product_with_ana = cls.env["product.product"].create(
            {
                "name": "WithAnalytic",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 20,
                "standard_price": 10,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "income_analytic_account_id": cls.ana_inc.id,
                "expense_analytic_account_id": cls.ana_exp.id,
            }
        )

    def test_income_account_branch(self):
        """Cover the case product_id + income_analytic_account_id."""
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_with_ana.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_with_ana.uom_id.id,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        line = so.order_line
        line._compute_analytic_distribution()
        self.assertEqual(line.analytic_distribution, {self.ana_inc.id: 100})

    def test_fallback_branch(self):
        """Cover the case product_id without any analytic account."""
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_no_ana.id,
                            "product_uom_qty": 1,
                            "product_uom": self.product_no_ana.uom_id.id,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        line = so.order_line
        line._compute_analytic_distribution()
        self.assertFalse(line.analytic_distribution)

    def test_no_product_branch(self):
        """Cover the case line.product_id = False."""
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "product_uom_qty": 1,
                "product_uom": self.product_no_ana.uom_id.id,
                "price_unit": 30,
            }
        )
        # Delete the product to force the branch without product_id
        line.product_id = False
        line._compute_analytic_distribution()
        self.assertFalse(line.analytic_distribution)
