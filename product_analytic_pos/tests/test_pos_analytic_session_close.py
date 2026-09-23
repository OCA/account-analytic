from odoo.tests import tagged

from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon, TestPoSCommon


@tagged("post_install", "-at_install")
class TestPosAnalyticSessionClose(TestPointOfSaleCommon, TestPoSCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref("analytic.group_analytic_accounting")
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "POS Products",
            }
        )
        cls.env["account.analytic.applicability"].create(
            {
                "business_domain": "general",
                "analytic_plan_id": cls.analytic_plan.id,
                "applicability": "mandatory",
            }
        )
        cls.product_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Product Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.category_analytic_account = cls.env["account.analytic.account"].create(
            {
                "name": "Category Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.category_with_distribution = cls.env["product.category"].create(
            {
                "name": "POS Analytic Category",
            }
        )
        cls.product_with_distribution = cls.create_product(
            "POS Product Distribution",
            cls.categ_basic,
            10.0,
            sale_account=cls.sale_account,
        )
        cls.product_with_category_distribution = cls.create_product(
            "POS Category Distribution",
            cls.category_with_distribution,
            15.0,
            sale_account=cls.sale_account,
        )
        cls.env["account.analytic.distribution.model"].create(
            {
                "product_id": cls.product_with_distribution.id,
                "analytic_distribution": {cls.product_analytic_account.id: 100},
            }
        )
        cls.env["account.analytic.distribution.model"].create(
            {
                "product_categ_id": cls.category_with_distribution.id,
                "analytic_distribution": {cls.category_analytic_account.id: 100},
            }
        )

    def setUp(self):
        super().setUp()
        self.config = self.basic_config
        self.config.payment_method_ids.filtered_domain(
            [("type", "=", "cash")]
        ).split_transactions = False
        self.session = self.open_new_session()

    def _create_order(self, products):
        order_data = self.create_ui_order_data([(product, 1) for product in products])
        order = self.env["pos.order"].sync_from_ui([order_data])
        return self.env["pos.order"].browse(int(order["pos.order"][0]["id"]))

    def _close_session(self):
        self.session.post_closing_cash_details(self.session.order_ids.amount_total)
        self.session.close_session_from_ui()

    def test_close_session_splits_sales_lines_by_distribution(self):
        self._create_order(
            [self.product_with_distribution, self.product_with_category_distribution]
        )

        self._close_session()

        sale_lines = self.session.move_id.line_ids.filtered(
            lambda line: line.display_type == "product"
            and line.account_id == self.sale_account
        )

        self.assertEqual(len(sale_lines), 2)
        self.assertEqual(
            {frozenset(line.analytic_distribution.items()) for line in sale_lines},
            {
                frozenset({str(self.product_analytic_account.id): 100.0}.items()),
                frozenset({str(self.category_analytic_account.id): 100.0}.items()),
            },
        )

    def test_close_session_uses_category_distribution_fallback(self):
        self._create_order([self.product_with_category_distribution])

        self._close_session()

        sale_line = self.session.move_id.line_ids.filtered(
            lambda line: line.display_type == "product"
            and line.account_id == self.sale_account
        )
        self.assertEqual(len(sale_line), 1)
        self.assertEqual(
            sale_line.analytic_distribution,
            {str(self.category_analytic_account.id): 100.0},
        )
