# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestSaleAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ana_inc = cls.env["account.analytic.account"].create(
            {"name": "Income Analytic"}
        )
        cls.ana_cat = cls.env["account.analytic.account"].create(
            {"name": "Category Analytic"}
        )

        cls.dist_cat = cls.env["account.analytic.distribution"].create(
            {
                "name": "Cat Dist",
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "Prod Dist",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 10,
                "standard_price": 5,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "analytic_account_id": cls.ana_inc.id,
                "analytic_distribution_id": cls.dist_cat.id,
            }
        )

        cls.product_no = cls.env["product.product"].create(
            {
                "name": "Prod NoAna",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "list_price": 5,
                "standard_price": 2,
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

    def _create_sale_line(self, product):
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        return so.order_line

    def test_with_product_and_distribution(self):
        """Branch: product_id + analytic_distribution_id + analytic_account_id"""
        line = self._create_sale_line(self.product)
        line._compute_analytic_distribution()
        self.assertEqual(line.analytic_distribution_id, self.dist_cat)

        inv_vals = line._prepare_invoice_line()
        self.assertEqual(inv_vals.get("analytic_account_id"), self.ana_inc.id)
        self.assertEqual(inv_vals.get("analytic_distribution_id"), self.dist_cat.id)

    def test_with_product_no_distribution(self):
        """Branch: product_id sense analytic_distribution_id però amb fallback categoria"""
        self.product_no.categ_id.analytic_distribution_id = self.dist_cat.id
        line = self._create_sale_line(self.product_no)
        line._compute_analytic_distribution()
        self.assertEqual(line.analytic_distribution_id, self.dist_cat)

    def test_without_product(self):
        """Branch: línia sense product_id"""
        so = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
            }
        )

        line = self.env["sale.order.line"].create(
            {
                "order_id": so.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "price_unit": 50,
            }
        )
        line.product_id = False
        line._compute_analytic_distribution()
        self.assertFalse(line.analytic_distribution_id)
        inv_vals = line._prepare_invoice_line()
        self.assertNotIn("analytic_account_id", inv_vals)
        self.assertNotIn("analytic_distribution_id", inv_vals)
