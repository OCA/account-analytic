# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockLandedCostsAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Product = self.env["product.product"]
        self.Picking = self.env["stock.picking"]
        self.LandedCost = self.env["stock.landed.cost"]
        self.ProductCategory = self.env["product.category"]
        self.Account = self.env["account.account"]

        self.analytic_distribution_1 = dict(
            {str(self.env.ref("analytic.analytic_agrolait").id): 100.0}
        )
        self.analytic_distribution_2 = dict(
            {str(self.env.ref("analytic.analytic_asustek").id): 100.0}
        )
        self.picking_type_in = self.env.ref("stock.picking_type_out")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")

        self.account_1 = self.Account.create(
            {
                "name": "Account 1 test",
                "code": "Account1",
                "account_type": self.env["account.account"]
                .search([], limit=1)
                .account_type,
                "reconcile": True,
            }
        )
        self.account_2 = self.Account.create(
            {
                "name": "Account 2 test",
                "code": "Account2",
                "account_type": self.env["account.account"]
                .search([], limit=1)
                .account_type,
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
                "type": "consu",
                "standard_price": 1.0,
                "categ_id": self.category.id,
            }
        )
        self.landed_cost_product = self.Product.create(
            {"name": "Landed Cost Product Test", "type": "service"}
        )

        picking_vals = {
            "name": "Landed Cost Picking Test",
            "picking_type_id": self.picking_type_in.id,
            "location_id": self.supplier_location.id,
            "location_dest_id": self.customer_location.id,
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Move Test",
                        "product_id": self.product.id,
                        "product_uom_qty": 5,
                        "quantity": 5,
                        "product_uom": self.env.ref("uom.product_uom_unit").id,
                        "location_id": self.supplier_location.id,
                        "location_dest_id": self.customer_location.id,
                    },
                )
            ],
        }
        self.expenses_journal = self.env["account.journal"].create(
            {
                "name": "Vendor Bills - Test",
                "code": "TEXJ",
                "type": "purchase",
                "company_id": self.env.company.id,
                "refund_sequence": True,
            }
        )
        picking_landed_cost = self.Picking.create(picking_vals)
        landed_cost_vals = {
            "company_id": self.expenses_journal.company_id.id,
            "picking_ids": [picking_landed_cost.id],
            "account_journal_id": self.expenses_journal.id,
            "cost_lines": [
                (
                    0,
                    0,
                    {
                        "product_id": self.landed_cost_product.id,
                        "price_unit": 2.0,
                        "split_method": "equal",
                        "account_id": self.account_1.id,
                        "analytic_distribution": self.analytic_distribution_1,
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
                        "analytic_distribution": self.analytic_distribution_2,
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
                self.assertEqual(
                    line.analytic_distribution, self.analytic_distribution_1
                )
            if line.account_id == self.account_2:
                self.assertEqual(
                    line.analytic_distribution, self.analytic_distribution_2
                )
