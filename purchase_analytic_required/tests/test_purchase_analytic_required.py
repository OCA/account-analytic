# Copyright 2026 BADEP
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseAnalyticRequired(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = new_test_user(
            cls.env,
            "purchase_analytic_required_user",
            groups=(
                "base.group_user,"
                "purchase.group_purchase_user,"
                "analytic.group_analytic_accounting"
            ),
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Purchase Analytic Partner"}
        )
        analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Purchase Analytic Plan"}
        )
        analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Purchase Analytic Account", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution = {str(analytic_account.id): 100.0}

    def test_analytic_distribution_is_required_on_purchase_order_form(self):
        form = Form(
            self.env["purchase.order"]
            .with_user(self.user)
            .with_context(default_partner_id=self.partner.id),
        )
        distribution_fields = form._view["tree"].xpath(
            ".//field[@name='analytic_distribution']"
        )
        self.assertTrue(
            any(field.get("required") == "1" for field in distribution_fields)
        )

        form.analytic_distribution = self.analytic_distribution
        purchase_order = form.save()
        self.assertEqual(
            purchase_order.analytic_distribution, self.analytic_distribution
        )
