# Copyright 2025 Tecnativa - Christian Ramos
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPosAnalyticConfig(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account 2",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.warehouse1 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 1",
                "code": "WH1",
            }
        )
        cls.warehouse2 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 2",
                "code": "WH2",
            }
        )
        cls.warehouse3 = cls.env["stock.warehouse"].create(
            {
                "name": "Warehouse 3",
                "code": "WH3",
            }
        )
        cls.analytic_distribution_model_1 = cls.env[
            "account.analytic.distribution.model"
        ].create(
            {
                "warehouse_id": cls.warehouse1.id,
                "analytic_distribution": {cls.analytic_account.id: 100.0},
            }
        )
        cls.analytic_distribution_model_2 = cls.env[
            "account.analytic.distribution.model"
        ].create(
            {
                "warehouse_id": cls.warehouse2.id,
                "analytic_distribution": {cls.analytic_account2.id: 100.0},
            }
        )
        cls.partner_a = cls.env["res.partner"].create({"name": "Partner A"})
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "list_price": 100.0,
            }
        )

    def _create_order(self, warehouse):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "warehouse_id": warehouse.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_a.id, "product_uom_qty": 1}
                    )
                ],
            }
        )

    def test_create_sale_order(self):
        order = self._create_order(self.warehouse1)
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        order2 = self._create_order(self.warehouse2)
        self.assertEqual(
            order2.order_line.analytic_distribution,
            {str(self.analytic_account2.id): 100.0},
        )

    def _add_line(self, order):
        line_before = order.order_line
        order.write(
            {
                "order_line": [
                    Command.create(
                        {"product_id": self.product_a.id, "product_uom_qty": 1}
                    )
                ]
            }
        )
        return order.order_line - line_before

    def test_change_warehouse_with_model(self):
        order = self._create_order(self.warehouse1)
        line1 = order.order_line
        self.assertEqual(
            line1.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        # The new warehouse has a distribution model, so it takes over the lines
        # added before the change, leaving no trace of the previous distribution
        order.warehouse_id = self.warehouse2
        line2 = self._add_line(order)
        self.assertEqual(
            line1.analytic_distribution,
            {str(self.analytic_account2.id): 100.0},
        )
        self.assertEqual(
            line2.analytic_distribution,
            {str(self.analytic_account2.id): 100.0},
        )

    def test_change_warehouse_without_model(self):
        order = self._create_order(self.warehouse1)
        line1 = order.order_line
        self.assertEqual(
            line1.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        # The new warehouse is absent from the models, so there's nothing to
        # apply: the previous line keeps its distribution and the new one,
        # having none to preserve, gets no distribution at all
        order.warehouse_id = self.warehouse3
        line2 = self._add_line(order)
        self.assertEqual(
            line1.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        self.assertFalse(line2.analytic_distribution)
