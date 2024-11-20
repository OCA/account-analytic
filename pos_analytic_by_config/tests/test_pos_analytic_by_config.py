# Copyright 2015 ACSONE SA/NV
# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon, TestPoSCommon


@tagged("post_install", "-at_install")
class TestPosAnalyticConfig(TestPointOfSaleCommon, TestPoSCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("analytic.group_analytic_accounting")
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Stores",
            }
        )
        cls.env["account.analytic.applicability"].create(
            {
                "business_domain": "general",
                "analytic_plan_id": cls.analytic_plan.id,
                "applicability": "mandatory",
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Test Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.env["account.analytic.distribution.model"].create(
            {
                "account_prefix": cls.sales_account.code,
                "pos_config_id": cls.basic_config.id,
                "analytic_distribution": {cls.analytic_account.id: 100},
            }
        )
        cls.config = cls.basic_config
        # Set the cash payment method to False for split transactions
        cls.config.payment_method_ids.filtered_domain(
            [("type", "=", "cash")]
        ).split_transactions = False
        cls.session = cls.open_new_session(cls)

    def _create_order(self):
        order_data = self.create_ui_order_data([(self.product_a, 1)])
        order = self.env["pos.order"].sync_from_ui([order_data])
        self.pos_order = self.env["pos.order"].browse(int(order["pos.order"][0]["id"]))

    def _close_session(self, amount_paid):
        self.session.post_closing_cash_details(amount_paid)
        self.session.close_session_from_ui()

    def test_order_simple_receipt(self):
        """Simple tickets are grouped by account in single move lines"""
        self._create_order()
        aml_domain = [
            ("account_id", "=", self.sales_account.id),
        ]
        # There aren't lines with the analytic account yet
        self.assertFalse(
            self.env["account.move.line"].search(aml_domain).analytic_distribution
        )
        self._close_session(self.pos_order.amount_total)
        # There they are
        self.assertEqual(
            self.env["account.move.line"].search(aml_domain).analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )

    def test_order_invoice(self):
        """Tickets with invoice are posted prior to session reconcilation"""
        self._create_order()
        self.pos_order.partner_id = self.partner_a
        aml_domain = [
            ("account_id", "=", self.sales_account.id),
            ("product_id", "=", self.product_a.id),
        ]
        lines = self.env["account.move.line"].search(aml_domain)
        # There aren't lines with the analytic account yet
        self.assertEqual(len(lines), 0)
        self.pos_order.action_pos_order_invoice()
        lines = self.env["account.move.line"].search(aml_domain)
        # There they are
        self.assertEqual(
            self.env["account.move.line"].search(aml_domain).analytic_distribution,
            {str(self.analytic_account.id): 100.0},
        )
