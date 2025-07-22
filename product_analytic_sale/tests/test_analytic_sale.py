from odoo.tests.common import TransactionCase


class TestAnalyticDistribution(TransactionCase):
    def setUp(self):
        super().setUp()
        plan = self.env["account.analytic.plan"].create({"name": "P"})
        self.ana = self.env["account.analytic.account"].create(
            {"name": "A", "plan_id": plan.id}
        )
        self.ana2 = self.env["account.analytic.account"].create(
            {"name": "B", "plan_id": plan.id}
        )

        self.prod_with = self.env["product.product"].create(
            {
                "name": "With",
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
                "income_analytic_account_id": self.ana.id,
            }
        )
        self.prod_without = self.env["product.product"].create(
            {
                "name": "Without",
                "type": "service",
                "uom_id": self.env.ref("uom.product_uom_hour").id,
                "uom_po_id": self.env.ref("uom.product_uom_hour").id,
            }
        )

        self.partner = self.env.ref("base.res_partner_1")

    def _make_so(self, product):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": product.name,
                            "product_uom_qty": 1,
                            "product_uom": product.uom_id.id,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )

    def test_with_income_account(self):
        so = self._make_so(self.prod_with)
        line = so.order_line
        self.assertEqual(
            list(line.analytic_distribution.keys()),
            [str(self.ana.id)],
        )

    def test_no_income_account_calls_super_empty(self):
        so = self._make_so(self.prod_without)
        line = so.order_line
        self.assertFalse(line.analytic_distribution)

    def test_distribution_model_applied(self):
        self.env["account.analytic.distribution.model"].create(
            {
                "product_id": self.prod_without.id,
                "analytic_distribution": {self.ana2.id: 100.0},
            }
        )
        so = self._make_so(self.prod_without)
        line = so.order_line
        self.assertEqual(list(line.analytic_distribution.keys()), [str(self.ana2.id)])
