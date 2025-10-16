#  Copyright (c) 2025 Groupe Voltaire
#  @author Guillaume MASSON <guillaume.masson@groupevoltaire.com>
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAnalyticDistributionByTeam(AccountTestInvoicingCommon):
    """
    Test suite for the account_analytic_distribution_team module.
    It ensures that analytic distribution models are correctly applied based on the sales team.
    """

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # === Create Analytic Plan (Required in Odoo 16+) ===
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Test Analytic Plan",
            }
        )

        # === Create Analytic Accounts (Now linked to the plan) ===
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Account 1",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic Account 2",
                "plan_id": cls.analytic_plan.id,
            }
        )
        cls.analytic_account_generic = cls.env["account.analytic.account"].create(
            {
                "name": "Generic Analytic Account",
                "plan_id": cls.analytic_plan.id,
            }
        )

        # === Create Sales Teams ===
        cls.team_a = cls.env["crm.team"].create({"name": "Sales Team A"})
        cls.team_b = cls.env["crm.team"].create({"name": "Sales Team B"})

        # === Create Products ===
        cls.product_with_rule = cls.env["product.product"].create(
            {
                "name": "Product with specific rule",
                "lst_price": 100.0,
                "standard_price": 80.0,
                "property_account_income_id": cls.company_data[
                    "default_account_revenue"
                ].id,
            }
        )

        # === Create Analytic Distribution Models ===

        # Generic Model (based on product only)
        cls.env["account.analytic.distribution.model"].create(
            {
                "product_id": cls.product_with_rule.id,
                "analytic_distribution": {
                    str(cls.analytic_account_generic.id): 100.00,
                },
            }
        )

        # Specific Model for Sales Team A (60/40 split)
        cls.team_a_dist_model = cls.env["account.analytic.distribution.model"].create(
            {
                "team_id": cls.team_a.id,
                "analytic_distribution": {
                    str(cls.analytic_account_1.id): 60.00,
                    str(cls.analytic_account_2.id): 40.00,
                },
            }
        )

    def _create_invoice_and_get_line(self, sales_team=False):
        """Helper to create a customer invoice and return the relevant line."""
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as move_form:
            move_form.partner_id = self.partner_a
            if sales_team:
                move_form.team_id = sales_team
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = self.product_with_rule
                line_form.quantity = 1
                line_form.price_unit = 100.0
        invoice = move_form.save()
        return invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.product_with_rule
        )

    def test_01_distribution_applied_for_matching_team(self):
        """
        Tests that an invoice assigned to Sales Team A gets the analytic
        distribution defined for that team.
        """
        invoice_line = self._create_invoice_and_get_line(sales_team=self.team_a)

        self.assertTrue(
            invoice_line.analytic_distribution, "Analytic distribution should be set."
        )
        self.assertEqual(
            invoice_line.analytic_distribution,
            self.team_a_dist_model.analytic_distribution,
            "The distribution should match the model for Sales Team A.",
        )

    def test_02_no_distribution_for_unmatching_team(self):
        """
        Tests that an invoice for Sales Team B (which has no specific model)
        falls back to the generic product-based rule.
        """
        invoice_line = self._create_invoice_and_get_line(sales_team=self.team_b)

        self.assertTrue(
            invoice_line.analytic_distribution,
            "Analytic distribution should be set from the generic rule.",
        )
        self.assertIn(
            str(self.analytic_account_generic.id),
            invoice_line.analytic_distribution,
            "The distribution should fall back to the generic product rule.",
        )
        self.assertEqual(
            invoice_line.analytic_distribution[str(self.analytic_account_generic.id)],
            100.00,
        )

    def test_03_specificity_team_over_product(self):
        """
        Tests that a rule with a Sales Team is more specific and overrides
        a rule based only on the product.
        """
        # We add another specific rule for the product AND the team, to ensure
        # it is chosen over the one with only the team
        specific_model = self.env["account.analytic.distribution.model"].create(
            {
                "team_id": self.team_a.id,
                "product_id": self.product_with_rule.id,
                "analytic_distribution": {
                    str(self.analytic_account_1.id): 100.00,
                },
            }
        )

        invoice_line = self._create_invoice_and_get_line(sales_team=self.team_a)

        self.assertTrue(
            invoice_line.analytic_distribution, "Analytic distribution should be set."
        )
        self.assertEqual(
            invoice_line.analytic_distribution,
            specific_model.analytic_distribution,
            "The most specific rule (Team + Product) should be applied.",
        )

    def test_04_no_distribution_when_no_team_on_invoice(self):
        """
        Tests that an invoice with no sales team assigned does not use the
        team-specific rule and falls back to the generic product-based rule.
        """
        invoice_line = self._create_invoice_and_get_line(sales_team=False)

        self.assertTrue(
            invoice_line.analytic_distribution,
            "Analytic distribution should fall back to the generic rule.",
        )
        self.assertNotIn(
            str(self.analytic_account_1.id),
            invoice_line.analytic_distribution,
            "Team A's distribution model should NOT be applied.",
        )
        self.assertIn(
            str(self.analytic_account_generic.id),
            invoice_line.analytic_distribution,
            "The distribution should fall back to the generic product rule.",
        )
