from odoo.tests.common import TransactionCase


class TestAnalyticPlan(TransactionCase):
    def setUp(self):
        super().setUp()

        AnalyticPlan = self.env["account.analytic.plan"]
        self.plan_customer = AnalyticPlan.create({"name": "Customer"})
        self.plan_product = AnalyticPlan.create({"name": "Product"})

        AnalyticAccount = self.env["account.analytic.account"]
        self.analyticA1 = AnalyticAccount.create(
            {"name": "Customer 1", "plan_id": self.plan_customer.id}
        )
        self.analyticB1 = AnalyticAccount.create(
            {"name": "Product 1", "plan_id": self.plan_product.id}
        )

        self.AnalyticModel = self.env["account.analytic.distribution.model"]
        self.some_partner = self.env["res.partner"].create({"name": "Some Partner"})
        self.some_product = self.env["product.product"].create({"name": "Some Product"})
        vals = [
            {
                "partner_id": self.some_partner.id,
                "analytic_distribution": {self.analyticA1.id: 100},
            },
            {
                "product_id": self.some_product.id,
                "analytic_distribution": {self.analyticB1.id: 100},
            },
        ]
        self.distribution_models = self.AnalyticModel.create(vals)

    def test_merged_default_plans(self):
        vals = {
            "company_id": 1,
            "partner_id": self.some_partner.id,
            "product_id": self.some_product.id,
        }
        res = self.AnalyticModel._get_distribution(vals)
        self.assertTrue(
            str(self.analyticA1.id) in res.keys(), "Customer Analytic applied"
        )
        self.assertTrue(
            str(self.analyticB1.id) in res.keys(), "Product Analytic applied"
        )
