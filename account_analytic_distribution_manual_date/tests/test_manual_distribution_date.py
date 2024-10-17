# Copyright 2024 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, datetime

from freezegun import freeze_time

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestManualDistributionDate(TransactionCase):
    @classmethod
    @freeze_time("2024-01-01")
    def setUpClass(cls):
        super().setUpClass()

        cls.manual_distribution = cls.env[
            "account.analytic.distribution.manual"
        ].create(
            {
                "name": "Test",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        )

        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Product A",
                            "quantity": 1,
                            "price_unit": 100.0,
                            "manual_distribution_id": cls.manual_distribution.id,
                        },
                    )
                ],
            }
        )

    @freeze_time("2024-01-01")
    def test_assert_date_time(self):
        """Check that date is 2024-01-01"""
        assert datetime.now() == datetime(2024, 1, 1)

    @freeze_time("2024-01-01")
    def test_write_without_invoice_date(self):
        """Test valid date within manual distribution range."""
        self.invoice.write(
            {
                "invoice_line_ids": [
                    (
                        1,
                        self.invoice.invoice_line_ids[0].id,
                        {
                            "manual_distribution_id": self.manual_distribution.id,
                        },
                    )
                ]
            }
        )

        updated_distribution_id = self.invoice.invoice_line_ids[
            0
        ].manual_distribution_id.id
        self.assertEqual(self.manual_distribution.id, updated_distribution_id)

    @freeze_time("2024-01-01")
    def test_write_with_valid_date(self):
        """Test valid date within manual distribution range."""
        new_date = "2024-07-01"
        self.invoice.write({"invoice_date": new_date})
        self.assertEqual(self.invoice.invoice_date, date.fromisoformat(new_date))

    @freeze_time("2024-01-01")
    def test_write_with_date_outside_distribution_range(self):
        """Test write raises UserError when date is outside the distribution range."""
        with self.assertRaises(UserError):
            self.invoice.write(
                {
                    "invoice_line_ids": [
                        (
                            1,
                            self.invoice.invoice_line_ids[0].id,
                            {
                                "manual_distribution_id": self.manual_distribution.id,
                            },
                        )
                    ],
                    "invoice_date": "2025-01-01",
                }
            )

    @freeze_time("2024-01-01")
    def test_write_without_date_outside_distribution_range(self):
        """
        Test write raises UserError when invoice date is not changed
        and it's outside distribution range.
        """
        self.manual_distribution.write(
            {"start_date": "2024-08-01", "end_date": "2024-08-31"}
        )

        with self.assertRaises(UserError):
            self.invoice.write(
                {
                    "invoice_line_ids": [
                        (
                            1,
                            self.invoice.invoice_line_ids[0].id,
                            {
                                "manual_distribution_id": self.manual_distribution.id,
                            },
                        )
                    ]
                }
            )

    @freeze_time("2024-01-01")
    def test_write_with_invoice_date_without_lines(self):
        """
        Tests saving a invoice only changing the invoice date
        """
        self.manual_distribution.write(
            {"start_date": "2024-08-01", "end_date": "2024-08-31"}
        )
        self.invoice.write({"invoice_date": "2024-08-03"})

        self.assertEqual(
            self.invoice.invoice_line_ids[0].manual_distribution_id.id,
            self.manual_distribution.id,
        )

    @freeze_time("2024-01-01")
    def test_write_with_invoice_date_outside_period(self):
        """
        Tests saving a invoice only changing the invoice date but
        outside the manual distribution period
        """
        self.manual_distribution.write(
            {"start_date": "2024-08-01", "end_date": "2024-08-31"}
        )

        with self.assertRaises(UserError):
            self.invoice.write({"invoice_date": "2024-09-04"})

    def test_write_without_invoice_date_with_new_distribution(self):
        """
        Test write without changing invoice_date when it's
        still valid within the distribution range.
        """

        new_distribution = self.env["account.analytic.distribution.manual"].create(
            {
                "name": "New Test Distribution",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            }
        )

        self.invoice.invoice_line_ids[0].manual_distribution_id = new_distribution

        self.invoice.write(
            {
                "invoice_line_ids": [
                    (
                        1,
                        self.invoice.invoice_line_ids[0].id,
                        {
                            "manual_distribution_id": new_distribution.id,
                        },
                    )
                ]
            }
        )

        updated_distribution_id = self.invoice.invoice_line_ids[
            0
        ].manual_distribution_id.id
        self.assertNotEqual(self.manual_distribution.id, updated_distribution_id)
