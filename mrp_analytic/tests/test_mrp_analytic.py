# Copyright 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common


class TestMrpAnalytic(common.TransactionCase):
    def setUp(self):
        super(TestMrpAnalytic, self).setUp()
        self.default_plan = self.env["account.analytic.plan"].create(
            {"name": "Default", "company_id": False}
        )
        self.analytic_account = self.env["account.analytic.account"].create(
            {
                "name": "Analytic account test",
                "plan_id": self.default_plan.id,
                "company_id": False,
            }
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
        self.production = (
            self.env["mrp.production"]
            .with_context(import_file=True)
            .create(
                {
                    "product_id": self.product.id,
                    "analytic_account_id": self.analytic_account.id,
                    "qty_producing": 1,
                    "product_uom_id": self.product.uom_id.id,
                    "bom_id": self.bom.id,
                }
            )
        )
        self.production.move_raw_ids.write({"quantity_done": 1})

    def test_num_productions(self):
        self.assertEqual(self.analytic_account.num_productions, 1)

    # def test_carry_to_move_line(self):
    #     self.production.button_mark_done()
    #     account_moves = self.env["account.move.line"].search(
    #         [("analytic_account_id", "=", self.analytic_account.id)]
    #     )
    #     self.assertEqual(len(account_moves), 4)
