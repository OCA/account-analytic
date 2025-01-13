# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.tests import Form, TransactionCase


class TestPurchaseAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("analytic.group_analytic_accounting")
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env.ref("product.product_product_9")
        cls.uom = cls.env.ref("uom.product_uom_unit")
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        analytic_account_manual = cls.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution_manual = {str(analytic_account_manual.id): 100}
        cls.analytic_distribution_manual2 = {str(analytic_account_manual.id): 50}

    def add_po_line(self, order, product=None):
        if not product:
            product = self.product
        order.order_line = [
            Command.create(
                {
                    "product_id": product.id,
                }
            )
        ]

    def test_analytic_distribution_with_create(self):
        """Create a purchase order (create)
        Set analytic distribution on purchase
        Check analytic distribution and line is set
        """
        po = self.env["purchase.order"].create({"partner_id": self.partner.id})

        # Test setting analytic distribution without order lines
        po.analytic_distribution = self.analytic_distribution_manual
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual)

        # Test setting analytic distribution with an order line
        self.add_po_line(po)
        po.analytic_distribution = self.analytic_distribution_manual2
        self.assertEqual(po.analytic_distribution, self.analytic_distribution_manual2)
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual2
        )

        # Test clearing analytic distribution with an order line
        po.analytic_distribution = False
        self.assertEqual(
            po.order_line.analytic_distribution, self.analytic_distribution_manual2
        )

    def test_analytic_distribution_with_form(self):
        """Create a purchase order (form)
        Set analytic distribution on purchase
        Check analytic distribution and line is set
        """
        order = Form(
            self.env["purchase.order"].with_context(default_partner_id=self.partner.id)
        )

        # Test setting analytic distribution without order lines
        order.analytic_distribution = self.analytic_distribution_manual
        self.assertEqual(order.analytic_distribution, self.analytic_distribution_manual)

        # Test setting analytic distribution with an order line
        order = order.save()
        self.add_po_line(order)
        with Form(order) as po:
            po.analytic_distribution = self.analytic_distribution_manual2
            self.assertEqual(
                po.analytic_distribution, self.analytic_distribution_manual2
            )
            self.assertEqual(
                po.order_line._field_value.get_vals(order.order_line.id)[
                    "analytic_distribution"
                ],
                self.analytic_distribution_manual2,
            )

            # Test clearing analytic distribution with an order line
            po.analytic_distribution = False
            self.assertEqual(
                po.order_line._field_value.get_vals(order.order_line.id)[
                    "analytic_distribution"
                ],
                self.analytic_distribution_manual2,
            )
