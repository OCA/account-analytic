# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestInventoryWarehouseAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.analytic_obj = cls.env["account.analytic.account"]
        cls.analytic_tag_obj = cls.env["account.analytic.tag"]
        cls.inventory_obj = cls.env["stock.inventory"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.quant_obj = cls.env["stock.quant"]
        cls.change_obj = cls.env["stock.change.product.qty"]
        cls.demo_user = cls.env.ref("base.user_demo")

        cls.demo_user.groups_id |= cls.env.ref("stock.group_stock_manager")

        vals = {"name": "Warehouse 0"}
        cls.analytic = cls.analytic_obj.create(vals)
        cls.tag = cls.analytic_tag_obj.create({"name": "WH0"})
        cls.warehouse.write(
            {
                "account_analytic_id": cls.analytic.id,
                "account_analytic_tag_ids": [(4, cls.tag.id)],
            }
        )
        vals = {"name": "Product Inventory", "type": "product"}
        cls.product = cls.env["product.product"].create(vals)
        cls.inventory = cls.inventory_obj.create(
            {
                "name": cls.product.name,
                "location_ids": [(4, cls.warehouse.lot_stock_id.id)],
                "product_ids": [(4, cls.product.id)],
            }
        )

    def test_warehouse_analytic(self):
        self.inventory.action_start()
        inventory_line = self.env["stock.inventory.line"].with_context(
            default_is_editable=True,
            default_inventory_id=self.inventory.id,
            default_company_id=self.env.company.id,
            default_product_id=self.product.id,
        )
        line = inventory_line.create(
            {
                "location_id": self.warehouse.lot_stock_id.id,
                "product_id": self.product.id,
            }
        )
        self.assertEqual(
            self.analytic,
            line.analytic_account_id,
        )

    def test_change_quant_qty_tree(self):
        # Create a first quantity in stock to help simulate inventory
        quant = self.quant_obj.with_context(inventory_mode=True).create(
            {
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": 3.0,
                "product_id": self.product.id,
            }
        )
        view = self.env.ref("stock.view_stock_quant_tree_editable")
        # Do an inventory as manager (through the tree view)
        with Form(quant.with_context(inventory_mode=True), view) as quant_tree:
            quant_tree.inventory_quantity = 4.0
        move = self.env["stock.move"].search([("product_id", "=", self.product.id)])

        self.assertEqual(self.warehouse.account_analytic_id, move.analytic_account_id)
        self.assertEqual(self.tag, move.analytic_tag_ids)
        self.assertEqual(self.warehouse.account_analytic_tag_ids, move.analytic_tag_ids)

    def test_change_quant_qty(self):
        # Create a first quantity in stock to help simulate inventory
        self.quant_obj.with_context(inventory_mode=True).create(
            {
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": 3.0,
                "product_id": self.product.id,
            }
        )
        InventoryWizard = self.change_obj.with_user(self.demo_user)
        inventory_wizard = InventoryWizard.create(
            {
                "product_id": self.product.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "new_quantity": 50.0,
            }
        )
        inventory_wizard.change_product_qty()
        move = self.env["stock.move"].search([("product_id", "=", self.product.id)])

        self.assertEqual(self.warehouse.account_analytic_id, move.analytic_account_id)
        self.assertEqual(self.tag, move.analytic_tag_ids)
        self.assertEqual(self.warehouse.account_analytic_tag_ids, move.analytic_tag_ids)
