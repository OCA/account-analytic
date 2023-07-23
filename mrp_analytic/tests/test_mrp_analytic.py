# Copyright 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestMrpAnalytic(common.TransactionCase):
    def setUp(self):
        super(TestMrpAnalytic, self).setUp()
        self.analytic_account = self.env["account.analytic.account"].create(
            {"name": "Analytic account test"}
        )
        self.analytic_tag = self.env["account.analytic.tag"].create(
            {"name": "Analytic tag test"}
        )
        self.product_category = self.env.ref("product.product_category_all")
        self.product_category.write(
            {"property_cost_method": "standard", "property_valuation": "real_time"}
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Test product",
                "type": "product",
                "categ_id": self.product_category.id,
                "standard_price": 2.0,
            }
        )
        self.raw = self.env["product.product"].create(
            {
                "name": "Raw material",
                "type": "product",
                "categ_id": self.product_category.id,
                "standard_price": 1.0,
            }
        )
        self.bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "bom_line_ids": [(0, 0, {"product_id": self.raw.id, "product_qty": 1})],
            }
        )

    def test_carry_to_move_line(self):
        self.production = (
            self.env["mrp.production"]
            .with_context(import_file=True)
            .create(
                {
                    "product_id": self.product.id,
                    "analytic_account_id": self.analytic_account.id,
                    "analytic_tag_ids": [(6, 0, [self.analytic_tag.id])],
                    "qty_producing": 1,
                    "product_uom_id": self.product.uom_id.id,
                    "bom_id": self.bom.id,
                }
            )
        )
        self.production.move_raw_ids.write({"quantity_done": 1})
        self.production.button_mark_done()
        aml_analytic = self.env["account.move.line"].search(
            [("analytic_account_id", "=", self.analytic_account.id)]
        )
        self.assertEqual(len(aml_analytic), 4)
