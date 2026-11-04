# Copyright 2026 - TODAY, Cristiano Mafra Junior <cristiano.mafra@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import tagged

from odoo.addons.stock_request.tests.test_stock_request import TestStockRequest


@tagged("-at_install", "post_install")
class TestStockRequestAnalyticTag(TestStockRequest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_tag_1 = cls.env["account.analytic.tag"].create(
            {"name": "Test Tag 1"}
        )
        cls.analytic_tag_2 = cls.env["account.analytic.tag"].create(
            {"name": "Test Tag 2"}
        )
        # Create a test route for procurement
        supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.test_route = cls.env["stock.route"].create(
            {
                "name": "Test Stock Request Route",
                "product_selectable": True,
                "warehouse_selectable": True,
                "warehouse_ids": [(4, cls.warehouse.id)],
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Replenish WH/Stock from Suppliers",
                            "action": "pull",
                            "picking_type_id": cls.warehouse.in_type_id.id,
                            "location_src_id": supplier_location.id,
                            "location_dest_id": cls.warehouse.lot_stock_id.id,
                            "procure_method": "make_to_stock",
                        },
                    )
                ],
            }
        )
        cls.product.route_ids = [(4, cls.test_route.id)]

    def test_stock_request_with_tag(self):
        """Stock request with single analytic tag."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "analytic_tag_ids": [(6, 0, [self.analytic_tag_1.id])],
            }
        )
        self.assertIn(self.analytic_tag_1, request.analytic_tag_ids)
        self.assertNotIn(self.analytic_tag_2, request.analytic_tag_ids)

    def test_stock_request_with_multiple_tags(self):
        """Stock request with multiple analytic tags."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag_1.id, self.analytic_tag_2.id])
                ],
            }
        )
        self.assertIn(self.analytic_tag_1, request.analytic_tag_ids)
        self.assertIn(self.analytic_tag_2, request.analytic_tag_ids)

    def test_stock_request_without_tags(self):
        """Stock request without analytic tags."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
            }
        )
        self.assertFalse(request.analytic_tag_ids)
        self.assertNotIn(self.analytic_tag_1, request.analytic_tag_ids)
        self.assertNotIn(self.analytic_tag_2, request.analytic_tag_ids)

    def test_analytic_tags_copied_to_stock_moves(self):
        """Verify that analytic tags are copied to stock moves."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "analytic_tag_ids": [(6, 0, [self.analytic_tag_1.id])],
            }
        )
        request.action_confirm()
        moves = request.move_ids
        self.assertTrue(moves)
        self.assertSetEqual(
            set(moves.mapped("analytic_tag_ids").ids),
            {self.analytic_tag_1.id},
        )

    def test_analytic_tags_multiple_on_moves(self):
        """Verify multiple tags are copied to stock moves."""
        request = self.env["stock.request"].create(
            {
                "product_id": self.product.id,
                "product_uom_id": self.product.uom_id.id,
                "product_uom_qty": 10,
                "warehouse_id": self.warehouse.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "analytic_tag_ids": [
                    (6, 0, [self.analytic_tag_1.id, self.analytic_tag_2.id])
                ],
            }
        )
        request.action_confirm()
        moves = request.move_ids
        self.assertTrue(moves)
        self.assertSetEqual(
            set(moves.mapped("analytic_tag_ids").ids),
            {self.analytic_tag_1.id, self.analytic_tag_2.id},
        )
