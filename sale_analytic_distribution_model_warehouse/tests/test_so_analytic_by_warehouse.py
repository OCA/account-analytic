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

    def test_create_sale_order(self):
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "warehouse_id": self.warehouse1.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_a.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        self.assertEqual(
            order.order_line.analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
        order2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_a.id,
                "warehouse_id": self.warehouse2.id,
                "order_line": [
                    Command.create(
                        {"product_id": self.product_a.id, "product_uom_qty": 1}
                    )
                ],
            }
        )
        self.assertEqual(
            order2.order_line.analytic_distribution,
            {str(self.analytic_account2.id): 100.0},
        )
