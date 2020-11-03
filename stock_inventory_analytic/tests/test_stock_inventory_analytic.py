# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# Copyright 2019 brain-tec AG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInventoryAnalytic(TransactionCase):
    def setUp(self):
        super(TestInventoryAnalytic, self).setUp()

        # MODELS
        self.product_product_model = self.env["product.product"]
        self.product_category_model = self.env["product.category"]
        self.account_move_line_model = self.env["account.move.line"]
        self.account_analytic_tag = self.env["account.analytic.tag"]

        # INSTANCES
        self.analytic_tag_1 = self.account_analytic_tag.create(
            {"name": "Analytic Tag 1 (test)"}
        )
        self.analytic_tag_2 = self.account_analytic_tag.create(
            {"name": "Analytic Tag 1 (test)"}
        )
        self.stock_journal = self.env["account.journal"].create(
            {"name": "Stock Journal", "code": "STJTEST", "type": "general"}
        )
        self.valuation_account = self.env["account.account"].create(
            {
                "name": "Test stock valuation",
                "code": "tv",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_input_account = self.env["account.account"].create(
            {
                "name": "Test stock input",
                "code": "tsti",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.stock_output_account = self.env["account.account"].create(
            {
                "name": "Test stock output",
                "code": "tout",
                "user_type_id": self.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": self.env.ref("base.main_company").id,
            }
        )
        self.category = self.product_category_model.create(
            {
                "name": "Physical (test)",
                "property_cost_method": "standard",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": self.valuation_account.id,
                "property_stock_account_input_categ_id": self.stock_input_account.id,
                "property_stock_account_output_categ_id": self.stock_output_account.id,
                "property_stock_journal": self.stock_journal.id,
            }
        )
        self.product = self.product_product_model.create(
            {
                "name": "Product (test)",
                "type": "product",
                "categ_id": self.category.id,
                "price": 500,
                "standard_price": 1000,
            }
        )
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.analytic_account = self.env.ref("analytic.analytic_agrolait")
        self.company = self.env.user.company_id

        # CONFIG
        self.company.write(
            {
                "analytic_account_id": self.analytic_account.id,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag_1.id, self.analytic_tag_2.id])
                ],
            }
        )

    def test_inventory_adjustment_analytic(self):
        inventory = self.env["stock.inventory"].create(
            {
                "name": "add product",
                "location_ids": [(4, self.stock_location.id)],
                "product_ids": [(4, self.product.id)],
            }
        )
        inventory.action_start()
        self.assertEqual(len(inventory.line_ids), 0)

        self.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": self.product.id,
                "product_qty": 5,
                "location_id": self.stock_location.id,
            }
        )
        self.assertEqual(len(inventory.line_ids), 1)
        self.assertEqual(inventory.line_ids.theoretical_qty, 0)
        inventory.action_validate()

        # Checks that there exists one analytic line created with that account
        account_move_lines = self.account_move_line_model.search(
            [
                ("product_id", "=", self.product.id),
                ("analytic_account_id", "=", self.analytic_account.id),
            ]
        )
        self.assertIs(len(account_move_lines), 1)
        self.assertListEqual(
            account_move_lines.analytic_tag_ids.ids,
            [self.analytic_tag_1.id, self.analytic_tag_2.id],
        )
