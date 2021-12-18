# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestInventoryWarehouseAnalytic(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_obj = cls.env["account.analytic.account"]
        cls.inventory_obj = cls.env["stock.inventory"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        vals = {"name": "Warehouse 0"}
        cls.analytic = cls.analytic_obj.create(vals)
        cls.warehouse.write(
            {
                "account_analytic_id": cls.analytic.id,
            }
        )
        vals = {"name": "Product Inventory"}
        cls.product = cls.env["product.template"].create(vals)
        cls.inventory = cls.inventory_obj.create(
            {
                "name": cls.product.name,
                "location_ids": [(4, cls.warehouse.lot_stock_id.id)],
                "product_ids": [(4, cls.product.id)],
            }
        )

    def test_warehouse_analytic(self):
        with Form(
            self.inventory.with_context(
                default_location_id=self.warehouse.lot_stock_id.id
            )
        ) as inventory_form:
            with inventory_form.line_ids.new(
                {"product_id": self.product.id}
            ) as line_form:
                self.assertEqual(
                    self.analytic,
                    line_form.analytic_account_id,
                )
