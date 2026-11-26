# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestPurchaseAnalytic(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env.ref("base.res_partner_12")
        self.product_id = self.env.ref("product.product_product_9")
        self.uom_id = self.env.ref("uom.product_uom_unit")
        analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Plan Test", "company_id": False}
        )
        analytic_account_manual = self.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        self.analytic_distribution_manual = {str(analytic_account_manual.id): 100}

    def test_analytic_distribution(self):
        """Create a purchase order (create)
        Set analytic distribution on purchase
        Check analytic distribution and line is set
        """
        po = self.env["purchase.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id.name,
                            "product_id": self.product_id.id,
                            "product_qty": 1.0,
                            "product_uom": self.uom_id.id,
                            "price_unit": 121.0,
                            "date_planned": datetime.today(),
                        },
                    )
                ],
            }
        )
        po.analytic_distribution = self.analytic_distribution_manual
        po._onchange_analytic_distribution()
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual
        )

    def test_analytic_disctribution_with_new(self):
        """Create a purchase order (new)
        Set analytic distribution on purchase
        Check analytic distribution and line is set
        """
        po = self.env["purchase.order"].new(
            {
                "partner_id": self.partner_id.id,
                "analytic_distribution": self.analytic_distribution_manual,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.product_id.name,
                            "product_id": self.product_id.id,
                            "product_qty": 1.0,
                            "product_uom": self.uom_id.id,
                            "price_unit": 121.0,
                            "date_planned": datetime.today(),
                        },
                    )
                ],
            }
        )
        po._onchange_analytic_distribution()
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual
        )

    def _create_po(self, order_line):
        return self.env["purchase.order"].create(
            {"partner_id": self.partner_id.id, "order_line": order_line}
        )

    def _product_line(self):
        return {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "product_qty": 1.0,
            "product_uom": self.uom_id.id,
            "price_unit": 121.0,
            "date_planned": datetime.today(),
            "analytic_distribution": self.analytic_distribution_manual,
        }

    def test_display_type_lines_ignored(self):
        po = self._create_po([(0, 0, self._product_line())])
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)
        po.write(
            {
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "display_type": "line_section",
                            "name": "Section",
                            "product_qty": 0,
                        },
                    ),
                    (
                        0,
                        0,
                        {"display_type": "line_note", "name": "Note", "product_qty": 0},
                    ),
                ]
            }
        )
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)

    def test_new_line_inherits_distribution(self):
        po = self._create_po([(0, 0, self._product_line())])
        line = self._product_line()
        line.pop("analytic_distribution")
        po.write({"order_line": [(0, 0, line)]})
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)
        self.assertEqual(
            po.order_line.mapped("analytic_distribution"),
            [self.analytic_distribution_manual] * 2,
        )
