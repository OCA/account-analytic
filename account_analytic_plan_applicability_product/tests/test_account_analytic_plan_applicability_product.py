# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase


class TestAccountAnalyticPlanApplicabilityProduct(TransactionCase):
    def test_applicability(self):
        """Test that demo data makes the internal plan mandatory for expenses product"""
        applicability_line = self.env.ref(
            "analytic.analytic_plan_internal"
        ).applicability_ids.filtered(lambda x: x.product_ids)[:1]
        self.assertTrue(applicability_line)
        args = {
            "business_domain": "invoice",
            "product": self.env.ref("product.expense_product").id,
        }
        self.assertEqual(applicability_line._get_score(**args), 2)
        args.pop("product")
        self.assertEqual(applicability_line._get_score(**args), -1)
