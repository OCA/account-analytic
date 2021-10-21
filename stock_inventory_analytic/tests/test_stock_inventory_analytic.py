# Copyright 2019 ForgeFlow S.L.
# Copyright 2019 brain-tec AG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestInventoryAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # MODELS
        cls.product_product_model = cls.env["product.product"]
        cls.product_category_model = cls.env["product.category"]
        cls.account_move_line_model = cls.env["account.move.line"]
        cls.account_analytic_tag = cls.env["account.analytic.tag"]

        # INSTANCES
        cls.analytic_tag_1 = cls.account_analytic_tag.create(
            {"name": "Analytic Tag 1 (test)"}
        )
        cls.analytic_tag_2 = cls.account_analytic_tag.create(
            {"name": "Analytic Tag 1 (test)"}
        )
        cls.stock_journal = cls.env["account.journal"].create(
            {"name": "Stock Journal", "code": "STJTEST", "type": "general"}
        )
        cls.valuation_account = cls.env["account.account"].create(
            {
                "name": "Test stock valuation",
                "code": "tv",
                "user_type_id": cls.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.stock_input_account = cls.env["account.account"].create(
            {
                "name": "Test stock input",
                "code": "tsti",
                "user_type_id": cls.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.stock_output_account = cls.env["account.account"].create(
            {
                "name": "Test stock output",
                "code": "tout",
                "user_type_id": cls.env["account.account.type"].search([], limit=1).id,
                "reconcile": True,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.category = cls.product_category_model.create(
            {
                "name": "Physical (test)",
                "property_cost_method": "standard",
                "property_valuation": "real_time",
                "property_stock_valuation_account_id": cls.valuation_account.id,
                "property_stock_account_input_categ_id": cls.stock_input_account.id,
                "property_stock_account_output_categ_id": cls.stock_output_account.id,
                "property_stock_journal": cls.stock_journal.id,
            }
        )
        cls.product = cls.product_product_model.create(
            {
                "name": "Product (test)",
                "type": "product",
                "categ_id": cls.category.id,
                "price": 500,
                "standard_price": 1000,
            }
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.analytic_account = cls.env.ref("analytic.analytic_agrolait")
        cls.company = cls.env.user.company_id

        # CONFIG
        cls.company.write(
            {
                "analytic_account_id": cls.analytic_account.id,
                "analytic_tag_ids": [
                    (6, 0, [cls.analytic_tag_1.id, cls.analytic_tag_2.id])
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
