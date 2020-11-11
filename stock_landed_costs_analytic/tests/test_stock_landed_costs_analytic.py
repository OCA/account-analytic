# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockLandedCostsAnalytic(TransactionCase):
    def setUp(self):
        super(TestStockLandedCostsAnalytic, self).setUp()
        self.Product = self.env["product.product"]
        self.Picking = self.env["stock.picking"]
        self.LandedCost = self.env["stock.landed.cost"]
        self.ProductCategory = self.env["product.category"]
        self.AnalyticTag = self.env["account.analytic.tag"]
        self.Account = self.env["account.account"]

        self.analytic_tag_1 = self.AnalyticTag.create({"name": "analytic tag test 1"})
        self.analytic_tag_2 = self.AnalyticTag.create({"name": "analytic tag test 2"})
        self.analytic_account_1 = self.env.ref("analytic.analytic_agrolait")
        self.analytic_account_2 = self.env.ref("analytic.analytic_asustek")
        self.account_1 = self.Account.create(
            {
                "name": "Account 1 test",
                "code": "Account1",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
            }
        )
        self.account_2 = self.Account.create(
            {
                "name": "Account 2 test",
                "code": "Account2",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
            }
        )
        self.category = self.ProductCategory.create(
            {
                "name": "Product Category Test",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        self.product = self.Product.create(
            {
                "name": "Product Test",
                "type": "product",
                "standard_price": 1.0,
                "categ_id": self.category.id,
            }
        )
        self.landed_cost_product = self.Product.create(
            {"name": "Landed Cost Product Test", "type": "service"}
        )
        picking_vals = {
            "name": "Landed Cost Picking Test",
            "picking_type_id": self.ref("stock.picking_type_out"),
            "location_id": self.ref("stock.stock_location_stock"),
            "location_dest_id": self.ref("stock.stock_location_customers"),
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": "Move Test",
                        "product_id": self.product.id,
                        "product_uom_qty": 5,
                        "product_uom": self.ref("uom.product_uom_unit"),
                    },
                )
            ],
        }
        picking_landed_cost = self.Picking.create(picking_vals)
        landed_cost_vals = {
            "picking_ids": [picking_landed_cost.id],
            "cost_lines": [
                (
                    0,
                    0,
                    {
                        "product_id": self.landed_cost_product.id,
                        "price_unit": 2.0,
                        "split_method": "equal",
                        "account_id": self.account_1.id,
                        "analytic_account_id": self.analytic_account_1.id,
                        "analytic_tag_ids": [(6, 0, self.analytic_tag_1.ids)],
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": self.landed_cost_product.id,
                        "price_unit": 4.0,
                        "split_method": "equal",
                        "account_id": self.account_2.id,
                        "analytic_account_id": self.analytic_account_2.id,
                        "analytic_tag_ids": [(6, 0, self.analytic_tag_2.ids)],
                    },
                ),
            ],
        }
        self.landed_cost = self.LandedCost.create(landed_cost_vals)

    def test_stock_landed_costs_analytic(self):
        self.landed_cost.button_validate()
        self.assertTrue(self.landed_cost.account_move_id)
        for line in self.landed_cost.account_move_id.line_ids:
            if line.account_id == self.account_1:
                self.assertEqual(line.analytic_tag_ids.ids, self.analytic_tag_1.ids)
                self.assertEqual(line.analytic_account_id, self.analytic_account_1)
            if line.account_id == self.account_2:
                self.assertEqual(line.analytic_tag_ids.ids, self.analytic_tag_2.ids)
                self.assertEqual(line.analytic_account_id, self.analytic_account_2)
