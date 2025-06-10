# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.exceptions import ValidationError
from odoo.fields import Date
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestDistributionModelDate(TransactionCase):
    @classmethod
    @freeze_time("2024-01-01")
    def setUpClass(cls):
        super().setUpClass()

        cls.analytic_plan_1 = cls.env["account.analytic.plan"].create(
            {
                "name": "Plan 1",
            }
        )

        cls.product = cls.env.ref("product.product_product_1")
        cls.financial_account = cls.product._get_product_accounts()["income"]

        cls.analytic_account_1 = cls.env["account.analytic.account"].create(
            {"name": "Account 1", "plan_id": cls.analytic_plan_1.id}
        )

        cls.partner_a = cls.env["res.partner"].create(
            {"name": "partner_a", "company_id": False}
        )
        cls.partner_b = cls.env["res.partner"].create(
            {"name": "partner_b", "company_id": False}
        )

        cls.distribution_1 = cls.env["account.analytic.distribution.model"].create(
            {
                "partner_id": cls.partner_a.id,
                "analytic_distribution": {cls.analytic_account_1.id: 100},
                "start_date": datetime.now().date() - timedelta(days=5),
                "end_date": datetime.now().date() + timedelta(days=5),
                "recalculate": True,
            }
        )

        cls.distribution_2 = cls.env["account.analytic.distribution.model"].create(
            {
                "partner_id": cls.partner_b.id,
                "analytic_distribution": {cls.analytic_account_1.id: 30},
                "start_date": datetime.now().date() + timedelta(days=5),
                "end_date": datetime.now().date() + timedelta(days=10),
                "recalculate": True,
            }
        )

        cls.partner = cls.env["res.partner"].create({"name": "Acme Corp"})
        cls.partner_category = cls.env["res.partner.category"].create({"name": "VIP"})
        cls.product = cls.env["product.product"].create({"name": "Product"})
        cls.product_categ = cls.env["product.category"].create({"name": "Electro"})

    @freeze_time("2024-01-01")
    def test_constraints(self):
        distribution = self.env["account.analytic.distribution.model"].create(
            {
                "partner_id": self.partner_a.id,
            }
        )
        with self.assertRaises(ValidationError):
            distribution.start_date = datetime.now().date() - timedelta(days=5)
            distribution.end_date = datetime.now().date() + timedelta(days=5)
            distribution._check_duplicate_dates()

        with self.assertRaises(ValidationError):
            distribution.start_date = datetime.now().date() - timedelta(days=5)
            distribution._check_duplicate_dates()

        with self.assertRaises(ValidationError):
            distribution.end_date = datetime.now().date() + timedelta(days=3)
            distribution._check_duplicate_dates()

    @freeze_time("2024-01-01")
    def test_distribution_model_with_dates_inside_period(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_a.id,
                "move_type": "out_invoice",
                "invoice_date": datetime.now().date(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        self.assertEqual(invoice.line_ids[0].account_id, self.financial_account)
        self.assertEqual(
            invoice.line_ids[0].analytic_distribution,
            self.distribution_1.analytic_distribution,
        )

    @freeze_time("2024-01-01")
    def test_distribution_model_with_dates_outside_period(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.partner_b.id,
                "move_type": "out_invoice",
                "invoice_date": datetime.now().date(),
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

        self.assertFalse(
            invoice.line_ids[0].analytic_distribution,
        )

    @freeze_time("2024-01-01")
    def test_action_recalculate_analytic_lines_applies_changes(self):
        self.distribution_1.analytic_distribution = False

        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": datetime.now().date(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "account_id": self.financial_account.id,
                            "partner_id": self.partner_a.id,
                            "debit": 100.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "counter",
                            "account_id": self.financial_account.id,
                            "debit": 0.0,
                            "credit": 100.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        line = move.line_ids.filtered(lambda line: line.partner_id == self.partner_a)
        self.assertFalse(line.analytic_distribution)

        self.distribution_1.analytic_distribution = {
            self.analytic_account_1.id: 100,
        }

        with self.assertRaises(ValidationError):
            # Error when no prefix is defined
            self.distribution_1.action_recalculate_analytic_lines()

        self.distribution_1.account_prefix = self.financial_account.code

        result = self.distribution_1.action_recalculate_analytic_lines()

        self.assertEqual(
            line.analytic_distribution, self.distribution_1.analytic_distribution
        )
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn(
            "analytic lines have been recalculated", result["params"]["message"]
        )

    @freeze_time("2024-01-01")
    def test_action_recalculate_analytic_lines_no_applies_changes(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": datetime.now().date(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "account_id": self.financial_account.id,
                            "partner_id": self.partner_a.id,
                            "debit": 100.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "counter",
                            "account_id": self.financial_account.id,
                            "debit": 0.0,
                            "credit": 100.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        line = move.line_ids.filtered(lambda line: line.partner_id == self.partner_a)
        self.assertEqual(
            line.analytic_distribution, self.distribution_1.analytic_distribution
        )

        self.distribution_1.write(
            {
                "start_date": datetime.now().date() + timedelta(days=60),
                "end_date": datetime.now().date() + timedelta(days=120),
            }
        )
        self.distribution_1.analytic_distribution = False
        self.distribution_1.account_prefix = self.financial_account.code

        result = self.distribution_1.action_recalculate_analytic_lines()

        self.assertTrue(line.analytic_distribution)
        # Confirms that the distribution is not applied
        # because the date is out of the range
        self.assertFalse(
            line.analytic_distribution == self.distribution_1.analytic_distribution
        )
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn(
            "No analytic lines have been recalculated", result["params"]["message"]
        )

    @freeze_time("2024-01-01")
    def test_no_recalculate_lines_from_other_model(self):
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": datetime.now().date(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "account_id": self.financial_account.id,
                            "partner_id": self.partner_a.id,
                            "debit": 100.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "counter",
                            "account_id": self.financial_account.id,
                            "debit": 0.0,
                            "credit": 100.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        line = move.line_ids.filtered(lambda line: line.partner_id == self.partner_a)
        line.invoice_date = datetime.now().date() + timedelta(days=5)
        self.assertEqual(
            line.analytic_distribution, self.distribution_1.analytic_distribution
        )

        self.distribution_2.account_prefix = self.financial_account.code
        self.distribution_2.partner_id = self.partner_a.id
        result = self.distribution_2.action_recalculate_analytic_lines()

        self.assertEqual(line.partner_id, self.distribution_2.partner_id)
        self.assertEqual(line.invoice_date, self.distribution_2.start_date)
        self.assertEqual(line.account_id.code, self.distribution_2.account_prefix)

        self.assertIn(
            "No analytic lines have been recalculated", result["params"]["message"]
        )
        self.assertTrue(
            line.analytic_distribution != self.distribution_2.analytic_distribution
        )

    @freeze_time("2024-01-01")
    def test_display_name_full_info_with_dates(self):
        record = self.env["account.analytic.distribution.model"].create(
            {
                "account_prefix": "123",
                "partner_id": self.partner.id,
                "partner_category_id": self.partner_category.id,
                "product_id": self.product.id,
                "product_categ_id": self.product_categ.id,
                "start_date": Date.from_string("2024-01-01"),
                "end_date": Date.from_string("2024-12-31"),
            }
        )
        record._compute_display_name()

        self.assertEqual(
            record.display_name,
            "123 | Acme Corp | VIP | Product | Electro (2024-01-01 - 2024-12-31)",
        )

    @freeze_time("2024-01-01")
    def test_action_sync_lines(self):
        self.distribution_1.partner_id = False
        self.distribution_1.account_prefix = "123"
        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "date": datetime.now().date(),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line_to_sync",
                            "account_id": self.financial_account.id,
                            "partner_id": self.partner_a.id,
                            "debit": 100.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "counter_line",
                            "account_id": self.financial_account.id,
                            "debit": 0.0,
                            "credit": 100.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()

        self.assertFalse(move.line_ids[0].distribution_model_id)
        self.assertFalse(move.line_ids[1].distribution_model_id)

        self.distribution_1.partner_id = self.partner_a.id
        self.distribution_1.account_prefix = self.financial_account.code

        self.distribution_1.action_sync_lines()

        self.assertEqual(
            move.line_ids[0].distribution_model_id.id, self.distribution_1.id
        )
        self.assertFalse(move.line_ids[1].distribution_model_id)
