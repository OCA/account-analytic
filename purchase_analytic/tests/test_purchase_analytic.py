# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchaseAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env.ref("base.res_partner_12")
        self.product_id = self.env.ref("product.product_product_9")
        self.uom_id = self.env.ref("uom.product_uom_unit")
        analytic_plan = self.env["account.analytic.plan"].create({"name": "Plan Test"})
        analytic_account_manual = self.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        self.analytic_distribution_manual = {str(analytic_account_manual.id): 100}
        self.analytic_distribution_manual2 = {str(analytic_account_manual.id): 50}

    def add_new_order_line(self):
        return [
            Command.create(
                {
                    "name": self.product_id.name,
                    "product_id": self.product_id.id,
                    "product_qty": 1.0,
                    "product_uom": self.uom_id.id,
                    "price_unit": 121.0,
                    "date_planned": datetime.today(),
                }
            )
        ]

    def test_analytic_distribution_with_create(self):
        """Create a purchase order (create)
        Set analytic distribution on purchase
        Check analytic distribution and line is set
        """
        po = self.env["purchase.order"].create({"partner_id": self.partner_id.id})

        # Test setting analytic distribution without order lines
        po.analytic_distribution = self.analytic_distribution_manual
        po._onchange_analytic_distribution()
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)

        # Test setting analytic distribution with an order line
        po.order_line = self.add_new_order_line()
        po.analytic_distribution = self.analytic_distribution_manual2
        po._onchange_analytic_distribution()
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual2)
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual2
        )

        # Test clearing analytic distribution with an order line
        po.analytic_distribution = False
        po._onchange_analytic_distribution()
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual2
        )

    def test_analytic_distribution_with_new(self):
        """Create a purchase order (new)
        Set analytic distribution on purchase
        Check analytic distribution and line is set
        """
        po = self.env["purchase.order"].new({"partner_id": self.partner_id.id})

        # Test setting analytic distribution without order lines
        po.analytic_distribution = self.analytic_distribution_manual
        po._onchange_analytic_distribution()
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)

        # Test setting analytic distribution with an order line
        po.order_line = self.add_new_order_line()
        po.analytic_distribution = self.analytic_distribution_manual2
        po._onchange_analytic_distribution()
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual2)
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual2
        )

        # Test clearing analytic distribution with an order line
        po.analytic_distribution = False
        po._onchange_analytic_distribution()
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual2
        )
