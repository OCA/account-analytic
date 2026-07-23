# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.fields import Date
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAccountAnalyticDistributionModelRecalculate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Model = cls.env["account.analytic.distribution.model"]
        cls.Move = cls.env["account.move"]

        cls.date_before = Date.to_date("2025-12-31")
        cls.date_start = Date.to_date("2026-01-01")
        cls.date_inside = Date.to_date("2026-01-15")
        cls.date_end = Date.to_date("2026-01-31")
        cls.date_after = Date.to_date("2026-02-01")

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.other_partner = cls.env["res.partner"].create(
            {"name": "Other Test Partner"}
        )
        cls.partner_category = cls.env["res.partner.category"].create(
            {"name": "Analytic model category"}
        )
        cls.partner.category_id = [Command.link(cls.partner_category.id)]

        cls.product_category = cls.env["product.category"].create(
            {"name": "Analytic model products"}
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Analytic model product",
                "categ_id": cls.product_category.id,
            }
        )
        cls.other_product = cls.env["product.product"].create({"name": "Other product"})

        cls.plan_1 = cls.env["account.analytic.plan"].create({"name": "Plan 1"})
        cls.plan_2 = cls.env["account.analytic.plan"].create({"name": "Plan 2"})
        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "Analytic Account 1", "plan_id": cls.plan_1.id}
        )
        cls.analytic_account_1_bis = cls.env["account.analytic.account"].create(
            {"name": "Analytic Account 1 bis", "plan_id": cls.plan_1.id}
        )
        cls.analytic_account_2 = cls.env["account.analytic.account"].create(
            {"name": "Analytic Account 2", "plan_id": cls.plan_2.id}
        )

        cls.account = cls.env["account.account"].create(
            {
                "name": "Test Account",
                "code": "TEST",
                "account_type": "income_other",
                "company_ids": [Command.link(cls.env.company.id)],
            }
        )
        cls.assertTrue(cls.account, "An account is required to execute the tests")

        cls.other_account = cls.env["account.account"].create(
            {
                "name": "Other Test Account",
                "code": "OTHER",
                "account_type": "income_other",
                "company_ids": [Command.link(cls.env.company.id)],
            }
        )
        cls.assertTrue(
            cls.other_account,
            "A second account is required to execute the multiple-prefix tests",
        )

        cls.model = cls._create_model(
            partner_id=cls.partner.id,
            account_prefix=cls.account.code,
            analytic_distribution={str(cls.analytic_account_1.id): 100},
            start_date=cls.date_start,
            end_date=cls.date_end,
            recalculate=True,
        )

    @classmethod
    def _create_model(cls, **values):
        values.setdefault(
            "analytic_distribution", {str(cls.analytic_account_1.id): 100}
        )
        return cls.Model.create(values)

    def _distribution_arguments(self, **values):
        arguments = {
            "partner_id": self.partner.id,
            "partner_category_id": self.partner.category_id.ids,
            "account_prefix": self.account.code,
            "company_id": self.env.company.id,
            "product_id": False,
            "product_categ_id": False,
            "date": self.date_inside,
            "related_root_plan_ids": self.env["account.analytic.plan"],
        }
        arguments.update(values)
        return arguments

    def _create_move_line(
        self,
        *,
        account=None,
        partner=None,
        product=None,
        date=None,
        analytic_distribution=None,
    ):
        account = account or self.account
        partner = partner or self.partner
        date = date or self.date_inside
        line_values = {
            "name": "Test distribution line",
            "account_id": account.id,
            "partner_id": partner.id,
            "balance": 100.0,
        }
        if product:
            line_values["product_id"] = product.id
        if analytic_distribution is not None:
            line_values["analytic_distribution"] = analytic_distribution

        move = self.Move.create(
            {
                "move_type": "entry",
                "date": date,
                "line_ids": [
                    Command.create(line_values),
                    Command.create(
                        {
                            "name": "Counterpart",
                            "account_id": self.other_account.id,
                            "balance": -100.0,
                        }
                    ),
                ],
            }
        )
        return move.line_ids.filtered(
            lambda line: line.name == "Test distribution line"
        )

    def test_distribution_inside_date_range(self):
        distribution, models = self.Model._get_distribution_and_models(
            self._distribution_arguments()
        )
        self.assertEqual(models, self.model)
        self.assertEqual(distribution[str(self.analytic_account_1.id)], 100)

    def test_distribution_date_boundaries_are_inclusive(self):
        for test_date in (self.date_start, self.date_end):
            with self.subTest(test_date=test_date):
                distribution, models = self.Model._get_distribution_and_models(
                    self._distribution_arguments(date=test_date)
                )
                self.assertEqual(models, self.model)
                self.assertEqual(distribution[str(self.analytic_account_1.id)], 100)

    def test_distribution_outside_date_range(self):
        for test_date in (self.date_before, self.date_after):
            with self.subTest(test_date=test_date):
                distribution, models = self.Model._get_distribution_and_models(
                    self._distribution_arguments(date=test_date)
                )
                self.assertFalse(distribution)
                self.assertFalse(models)

    def test_model_without_dates_applies(self):
        model = self._create_model(
            partner_id=self.other_partner.id,
            account_prefix=self.account.code,
        )
        distribution, models = self.Model._get_distribution_and_models(
            self._distribution_arguments(partner_id=self.other_partner.id)
        )
        self.assertEqual(models, model)
        self.assertEqual(distribution[str(self.analytic_account_1.id)], 100)

    def test_model_with_only_start_date(self):
        model = self._create_model(
            partner_id=self.other_partner.id,
            account_prefix=self.account.code,
            start_date=self.date_start,
        )
        before_distribution, before_models = self.Model._get_distribution_and_models(
            self._distribution_arguments(
                partner_id=self.other_partner.id,
                date=self.date_before,
            )
        )
        inside_distribution, inside_models = self.Model._get_distribution_and_models(
            self._distribution_arguments(
                partner_id=self.other_partner.id,
                date=self.date_inside,
            )
        )
        self.assertFalse(before_distribution)
        self.assertFalse(before_models)
        self.assertEqual(inside_models, model)
        self.assertTrue(inside_distribution)

    def test_model_with_only_end_date(self):
        model = self._create_model(
            partner_id=self.other_partner.id,
            account_prefix=self.account.code,
            end_date=self.date_end,
        )
        inside_distribution, inside_models = self.Model._get_distribution_and_models(
            self._distribution_arguments(
                partner_id=self.other_partner.id,
                date=self.date_inside,
            )
        )
        after_distribution, after_models = self.Model._get_distribution_and_models(
            self._distribution_arguments(
                partner_id=self.other_partner.id,
                date=self.date_after,
            )
        )
        self.assertEqual(inside_models, model)
        self.assertTrue(inside_distribution)
        self.assertFalse(after_distribution)
        self.assertFalse(after_models)

    def test_missing_date_does_not_filter_models(self):
        distribution, models = self.Model._get_distribution_and_models(
            self._distribution_arguments(date=False)
        )
        self.assertEqual(models, self.model)
        self.assertTrue(distribution)

    def test_start_date_cannot_be_after_end_date(self):
        with self.assertRaises(ValidationError):
            self.model.write(
                {"start_date": self.date_after, "end_date": self.date_start}
            )

    def test_equal_start_and_end_dates_are_allowed(self):
        self.model.write({"start_date": self.date_inside, "end_date": self.date_inside})
        self.assertEqual(self.model.start_date, self.date_inside)
        self.assertEqual(self.model.end_date, self.date_inside)

    def test_overlapping_closed_intervals_are_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_model(
                partner_id=self.partner.id,
                account_prefix=self.account.code,
                start_date=Date.to_date("2026-01-10"),
                end_date=Date.to_date("2026-02-10"),
            )

    def test_open_interval_overlap_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._create_model(
                partner_id=self.partner.id,
                account_prefix=self.account.code,
                start_date=False,
                end_date=Date.to_date("2026-01-10"),
            )

        with self.assertRaises(ValidationError):
            self._create_model(
                partner_id=self.partner.id,
                account_prefix=self.account.code,
                start_date=Date.to_date("2026-01-20"),
                end_date=False,
            )

    def test_non_overlapping_intervals_are_allowed(self):
        previous = self._create_model(
            partner_id=self.partner.id,
            account_prefix=self.account.code,
            start_date=Date.to_date("2025-01-01"),
            end_date=self.date_before,
        )
        following = self._create_model(
            partner_id=self.partner.id,
            account_prefix=self.account.code,
            start_date=self.date_after,
            end_date=Date.to_date("2026-12-31"),
        )
        self.assertTrue(previous)
        self.assertTrue(following)

    def test_same_dates_with_different_conditions_are_allowed(self):
        different_partner = self._create_model(
            partner_id=self.other_partner.id,
            account_prefix=self.account.code,
            start_date=self.date_start,
            end_date=self.date_end,
        )
        different_prefix = self._create_model(
            partner_id=self.partner.id,
            account_prefix=self.other_account.code,
            start_date=self.date_start,
            end_date=self.date_end,
        )
        self.assertTrue(different_partner)
        self.assertTrue(different_prefix)

    def test_write_cannot_create_overlap(self):
        model = self._create_model(
            partner_id=self.partner.id,
            account_prefix=self.account.code,
            start_date=self.date_after,
            end_date=Date.to_date("2026-12-31"),
        )
        with self.assertRaises(ValidationError):
            model.write({"start_date": self.date_inside})

    def test_display_name_contains_conditions_and_dates(self):
        self.assertIn(self.account.code, self.model.display_name)
        self.assertIn(self.partner.name, self.model.display_name)
        self.assertIn(Date.to_string(self.date_start), self.model.display_name)
        self.assertIn(Date.to_string(self.date_end), self.model.display_name)

    def test_display_name_fallback(self):
        model = self._create_model(
            analytic_distribution={str(self.analytic_account_2.id): 100}
        )
        self.assertEqual(model.display_name, "Analytic Distribution Model")

    def test_related_root_plan_prevents_model_from_same_plan(self):
        distribution, models = self.Model._get_distribution_and_models(
            self._distribution_arguments(related_root_plan_ids=self.plan_1)
        )
        self.assertFalse(distribution)
        self.assertFalse(models)

    def test_related_root_plan_only_blocks_its_own_plan(self):
        model_plan_2 = self._create_model(
            partner_id=self.partner.id,
            account_prefix=self.account.code,
            product_id=self.product.id,
            analytic_distribution={str(self.analytic_account_2.id): 100},
            start_date=self.date_start,
            end_date=self.date_end,
        )
        distribution, models = self.Model._get_distribution_and_models(
            self._distribution_arguments(
                product_id=self.product.id,
                product_categ_id=self.product.categ_id.id,
                related_root_plan_ids=self.plan_1,
            )
        )
        self.assertEqual(models, model_plan_2)
        self.assertNotIn(str(self.analytic_account_1.id), distribution)
        self.assertEqual(distribution[str(self.analytic_account_2.id)], 100)

    def test_lines_domain_requires_recalculation(self):
        self.model.recalculate = False
        with self.assertRaises(ValidationError):
            self.model._get_lines_domain()

    def test_lines_domain_requires_partner_and_prefix(self):
        no_partner = self._create_model(
            account_prefix=self.other_account.code,
            recalculate=True,
            start_date=self.date_start,
            end_date=self.date_end,
        )
        with self.assertRaises(ValidationError):
            no_partner._get_lines_domain()

        no_prefix = self._create_model(
            partner_id=self.other_partner.id,
            recalculate=True,
            start_date=self.date_start,
            end_date=self.date_end,
        )
        with self.assertRaises(ValidationError):
            no_prefix._get_lines_domain()

    def test_lines_domain_accepts_multiple_account_prefixes(self):
        model = self._create_model(
            partner_id=self.other_partner.id,
            account_prefix=f"{self.account.code}, {self.other_account.code}",
            start_date=self.date_start,
            end_date=self.date_end,
            recalculate=True,
        )
        first_line = self._create_move_line(
            account=self.account,
            partner=self.other_partner,
        )
        second_line = self._create_move_line(
            account=self.other_account,
            partner=self.other_partner,
        )
        lines = self.env["account.move.line"].search(model._get_lines_domain())
        self.assertIn(first_line, lines)
        self.assertIn(second_line, lines)

    def test_lines_domain_filters_optional_conditions(self):
        model = self._create_model(
            partner_id=self.partner.id,
            partner_category_id=self.partner_category.id,
            account_prefix=self.account.code,
            product_id=self.product.id,
            product_categ_id=self.product_category.id,
            company_id=self.env.company.id,
            start_date=self.date_start,
            end_date=self.date_end,
            recalculate=True,
        )
        matching_line = self._create_move_line(product=self.product)
        wrong_product_line = self._create_move_line(product=self.other_product)
        lines = self.env["account.move.line"].search(model._get_lines_domain())
        self.assertIn(matching_line, lines)
        self.assertNotIn(wrong_product_line, lines)

    def test_sync_adds_matching_model(self):
        line = self._create_move_line()
        line.distribution_model_ids = [Command.clear()]

        updated = line._sync_distribution_models()

        self.assertEqual(updated, 1)
        self.assertEqual(line.distribution_model_ids, self.model)

    def test_sync_removes_model_that_no_longer_applies(self):
        line = self._create_move_line(partner=self.other_partner)
        line.distribution_model_ids = [Command.set(self.model.ids)]

        updated = line._sync_distribution_models()

        self.assertEqual(updated, 1)
        self.assertFalse(line.distribution_model_ids)

    def test_sync_without_changes_returns_zero(self):
        line = self._create_move_line()
        line._sync_distribution_models()

        self.assertEqual(line._sync_distribution_models(), 0)

    def test_recalculate_updates_distribution_and_models(self):
        line = self._create_move_line(analytic_distribution={})
        line.distribution_model_ids = [Command.clear()]

        updated = line._recompute_distribution_models()

        self.assertEqual(updated, 1)
        self.assertEqual(line.distribution_model_ids, self.model)
        self.assertEqual(
            line.analytic_distribution[str(self.analytic_account_1.id)], 100
        )

    def test_recalculate_preserves_related_distribution(self):
        related_distribution = {str(self.analytic_account_1_bis.id): 100}
        line = self._create_move_line(analytic_distribution=related_distribution)

        # Simulate a distribution supplied by another business document.
        with patch.object(
            type(line),
            "_related_analytic_distribution",
            autospec=True,
            return_value=related_distribution,
        ):
            updated = line._recompute_distribution_models()

        self.assertIn(str(self.analytic_account_1_bis.id), line.analytic_distribution)
        self.assertNotIn(str(self.analytic_account_1.id), line.analytic_distribution)
        self.assertFalse(line.distribution_model_ids)
        self.assertIn(updated, (0, 1))

    def test_recalculate_without_changes_returns_zero(self):
        line = self._create_move_line()
        line._recompute_distribution_models()

        self.assertEqual(line._recompute_distribution_models(), 0)

    def test_action_sync_lines(self):
        line = self._create_move_line()
        line.distribution_model_ids = [Command.clear()]

        action = self.model.action_sync_lines()

        self.assertEqual(line.distribution_model_ids, self.model)
        self.assertEqual(action["tag"], "display_notification")
        self.assertEqual(action["params"]["type"], "success")

    def test_action_recalculate_analytic_lines(self):
        line = self._create_move_line()
        line.distribution_model_ids = [Command.set(self.model.ids)]
        line.analytic_distribution = {
            str(self.analytic_account_1_bis.id): 100,
        }

        action = self.model.action_recalculate_analytic_lines()

        self.assertEqual(
            line.analytic_distribution[str(self.analytic_account_1.id)], 100
        )
        self.assertNotIn(
            str(self.analytic_account_1_bis.id), line.analytic_distribution
        )
        self.assertEqual(action["tag"], "display_notification")

    def test_notification_without_updates(self):
        action = self.model._notification_action(0, "Test title")
        self.assertEqual(action["params"]["title"], "Test title")
        self.assertEqual(
            action["params"]["message"], "No journal items have been updated."
        )
