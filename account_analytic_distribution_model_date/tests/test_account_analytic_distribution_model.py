# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.exceptions import ValidationError
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
            }
        )

        cls.distribution_2 = cls.env["account.analytic.distribution.model"].create(
            {
                "partner_id": cls.partner_b.id,
                "analytic_distribution": {cls.analytic_account_1.id: 30},
                "start_date": datetime.now().date() + timedelta(days=5),
                "end_date": datetime.now().date() + timedelta(days=10),
            }
        )

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
