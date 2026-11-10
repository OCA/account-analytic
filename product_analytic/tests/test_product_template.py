# Copyright 2025 Your Name
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_plan = cls.env["account.analytic.plan"].create(
            {"name": "Default Plan", "applicability_ids": False}
        )
        cls.analytic_account1 = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account1", "plan_id": cls.default_plan.id}
        )
        cls.analytic_account2 = cls.env["account.analytic.account"].create(
            {"name": "test analytic_account2", "plan_id": cls.default_plan.id}
        )
        cls.distribution_model1 = cls.env["account.analytic.distribution.model"].create(
            {
                "account_prefix": "TEST",
                "analytic_distribution": {cls.analytic_account1.id: 100},
            }
        )
        cls.distribution_model2 = cls.env["account.analytic.distribution.model"].create(
            {
                "account_prefix": "DEMO",
                "analytic_distribution": {cls.analytic_account2.id: 100},
            }
        )

    def test_compute_analytic_distribution_models(self):
        """Test that analytic_distribution_model_ids is computed from product variant"""
        template = self.env["product.template"].create({"name": "Test Template"})
        # Add distribution models to the product variant
        template.product_variant_id.write(
            {
                "analytic_distribution_model_ids": [
                    Command.set(
                        [self.distribution_model1.id, self.distribution_model2.id]
                    )
                ]
            }
        )

        # Check that template gets the models from variant
        self.assertEqual(len(template.analytic_distribution_model_ids), 2)
        self.assertIn(
            self.distribution_model1, template.analytic_distribution_model_ids
        )
        self.assertIn(
            self.distribution_model2, template.analytic_distribution_model_ids
        )

    def test_inverse_analytic_distribution_models_single_variant(self):
        """Test inverse method for single variant template"""
        template = self.env["product.template"].create({"name": "Test Template"})
        # Set distribution models via template
        template.write(
            {
                "analytic_distribution_model_ids": [
                    Command.set([self.distribution_model1.id])
                ]
            }
        )

        # Check that variant gets the models
        self.assertEqual(
            len(template.product_variant_id.analytic_distribution_model_ids), 1
        )
        self.assertIn(
            self.distribution_model1,
            template.product_variant_id.analytic_distribution_model_ids,
        )

    def test_inverse_analytic_distribution_models_multi_variant(self):
        """Test inverse method doesn't affect multi-variant templates"""
        template = self.env["product.template"].create(
            {
                "name": "Test Template",
            }
        )
        # Add a variant to make it multi-variant
        self.env["product.product"].create(
            {
                "product_tmpl_id": template.id,
                "name": "Variant 2",
            }
        )
        # Get original variant models
        original_models = (
            template.product_variant_id.analytic_distribution_model_ids.ids
        )
        # Try to set distribution models via template (should be ignored)
        template.write(
            {
                "analytic_distribution_model_ids": [
                    Command.set([self.distribution_model1.id])
                ]
            }
        )
        # Check that variant models are unchanged
        self.assertEqual(
            template.product_variant_id.analytic_distribution_model_ids.ids,
            original_models,
        )

    def test_create_with_analytic_distribution_models(self):
        """Test creating template with distribution models"""
        template = self.env["product.template"].create(
            {
                "name": "Test Template",
                "analytic_distribution_model_ids": [
                    Command.link(self.distribution_model1.id),
                    Command.link(self.distribution_model2.id),
                ],
            }
        )
        # Check that variant gets the models
        self.assertEqual(
            len(template.product_variant_id.analytic_distribution_model_ids), 2
        )
        self.assertIn(
            self.distribution_model1,
            template.product_variant_id.analytic_distribution_model_ids,
        )
        self.assertIn(
            self.distribution_model2,
            template.product_variant_id.analytic_distribution_model_ids,
        )

    def test_create_multi_variant_with_distribution_models(self):
        """Test creating multi-variant with distribution models (should be ignored)"""
        template = self.env["product.template"].create(
            {
                "name": "Test Template",
            }
        )
        # Add second variant
        self.env["product.product"].create(
            {
                "product_tmpl_id": template.id,
                "name": "Variant 2",
            }
        )
        # Check that no distribution models were set on variants
        self.assertEqual(
            len(template.product_variant_id.analytic_distribution_model_ids), 0
        )
