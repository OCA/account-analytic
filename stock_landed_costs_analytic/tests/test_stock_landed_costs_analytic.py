# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockLandedCostsAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.Product = cls.env["product.product"]
        cls.Picking = cls.env["stock.picking"]
        cls.LandedCost = cls.env["stock.landed.cost"]
        cls.ProductCategory = cls.env["product.category"]
        cls.Account = cls.env["account.account"]

        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Test Plan"})
        analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "Analytic Account 1 Test", "plan_id": analytic_plan.id}
        )
        analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "Analytic Account 2 Test", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution_1 = {str(analytic_account_1.id): 100.0}
        cls.analytic_distribution_2 = {str(analytic_account_2.id): 100.0}

        cls.picking_type_in = cls.env.ref("stock.picking_type_out")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        account_type = cls.env["account.account"].search([], limit=1).account_type
        cls.account_1 = cls.Account.create(
            {
                "name": "Account 1 test",
                "code": "Account1",
                "account_type": account_type,
                "reconcile": True,
            }
        )
        cls.account_2 = cls.Account.create(
            {
                "name": "Account 2 test",
                "code": "Account2",
                "account_type": account_type,
                "reconcile": True,
            }
        )
        cls.category = cls.ProductCategory.create(
            {
                "name": "Product Category Test",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        cls.product = cls.Product.create(
            {
                "name": "Product Test",
                "type": "consu",
                "standard_price": 1.0,
                "categ_id": cls.category.id,
            }
        )
        cls.landed_cost_product = cls.Product.create(
            {"name": "Landed Cost Product Test", "type": "service"}
        )

        cls.expenses_journal = cls.env["account.journal"].create(
            {
                "name": "Vendor Bills - Test",
                "code": "TEXJ",
                "type": "purchase",
                "company_id": cls.env.company.id,
                "refund_sequence": True,
            }
        )

        picking_vals = {
            "name": "Landed Cost Picking Test",
            "picking_type_id": cls.picking_type_in.id,
            "location_id": cls.supplier_location.id,
            "location_dest_id": cls.customer_location.id,
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Move Test",
                        "product_id": cls.product.id,
                        "product_uom_qty": 5,
                        "quantity": 5,
                        "product_uom": cls.env.ref("uom.product_uom_unit").id,
                        "location_id": cls.supplier_location.id,
                        "location_dest_id": cls.customer_location.id,
                    },
                )
            ],
        }
        picking_landed_cost = cls.Picking.create(picking_vals)
        landed_cost_vals = {
            "company_id": cls.expenses_journal.company_id.id,
            "picking_ids": [picking_landed_cost.id],
            "account_journal_id": cls.expenses_journal.id,
            "cost_lines": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.landed_cost_product.id,
                        "price_unit": 2.0,
                        "split_method": "equal",
                        "account_id": cls.account_1.id,
                        "analytic_distribution": cls.analytic_distribution_1,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "product_id": cls.landed_cost_product.id,
                        "price_unit": 4.0,
                        "split_method": "equal",
                        "account_id": cls.account_2.id,
                        "analytic_distribution": cls.analytic_distribution_2,
                    },
                ),
            ],
        }
        cls.landed_cost = cls.LandedCost.create(landed_cost_vals)

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
