# Copyright 2026 (APSL - Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, tagged
from odoo.tools.float_utils import float_compare

from odoo.addons.account_analytic_source_move_info.hooks import (
    _sql_backfill_analytic_percentage,
    _sql_backfill_source_move_amounts,
    _sql_backfill_source_move_currency_id,
    _sql_backfill_source_move_total_analytic_percentage,
)


@tagged("post_install", "-at_install")
class TestAccountAnalyticLineInvoiceInfo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company = cls.env.company

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

        cls.income_account = cls.env["account.account"].create(
            {
                "name": "Test Income",
                "code": "XTESTINC",
                "account_type": "income",
            }
        )

        cls.receivable_account = cls.env["account.account"].create(
            {
                "name": "Test Receivable",
                "code": "XTESTREC",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )

        cls.partner.property_account_receivable_id = cls.receivable_account

        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {
                "name": "Test Analytic Plan",
            }
        )

        cls.analytic_account_a = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic A",
                "plan_id": cls.analytic_plan.id,
                "company_id": cls.company.id,
            }
        )

        cls.analytic_account_b = cls.env["account.analytic.account"].create(
            {
                "name": "Analytic B",
                "plan_id": cls.analytic_plan.id,
                "company_id": cls.company.id,
            }
        )

    def _assert_float_equal(self, value, expected, precision_digits=2):
        self.assertEqual(
            float_compare(
                value,
                expected,
                precision_digits=precision_digits,
            ),
            0,
            f"{value} != {expected} with precision_digits={precision_digits}",
        )

    def _get_analytic_account_field_names_for_test(self):
        return [
            field_name
            for field_name, field in self.env["account.analytic.line"]._fields.items()
            if field.type == "many2one"
            and field.comodel_name == "account.analytic.account"
            and (field_name == "account_id" or field_name.startswith("x_plan"))
        ]

    def _analytic_line_has_account(self, line, analytic_account):
        for field_name in self._get_analytic_account_field_names_for_test():
            if line[field_name] == analytic_account:
                return True
        return False

    def _get_analytic_account_column_names_for_sql_hook(self):
        return self._get_analytic_account_field_names_for_test()

    def _create_invoice(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Line 1",
                            "quantity": 1.0,
                            "price_unit": 600.0,
                            "account_id": self.income_account.id,
                            "analytic_distribution": {
                                str(self.analytic_account_a.id): 50.0,
                                str(self.analytic_account_b.id): 50.0,
                            },
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Line 2",
                            "quantity": 1.0,
                            "price_unit": 400.0,
                            "account_id": self.income_account.id,
                            "analytic_distribution": {
                                str(self.analytic_account_a.id): 100.0,
                            },
                        },
                    ),
                ],
            }
        )
        invoice.action_post()
        return invoice

    def test_source_move_analytic_info_from_invoice_posting(self):
        invoice = self._create_invoice()

        analytic_lines = self.env["account.analytic.line"].search(
            [
                ("move_line_id.move_id", "=", invoice.id),
            ]
        )
        self.assertTrue(analytic_lines)

        invoice_line_1 = invoice.invoice_line_ids.filtered(
            lambda line: line.price_subtotal == 600.0
        )
        self.assertEqual(len(invoice_line_1), 1)

        analytic_line_a_line_1 = analytic_lines.filtered(
            lambda line: line.move_line_id == invoice_line_1
            and self._analytic_line_has_account(line, self.analytic_account_a)
        )
        self.assertEqual(len(analytic_line_a_line_1), 1)

        self.assertEqual(
            analytic_line_a_line_1.source_move_currency_id,
            invoice.currency_id,
        )

        self._assert_float_equal(
            analytic_line_a_line_1.analytic_percentage,
            50.0,
        )

        self._assert_float_equal(
            analytic_line_a_line_1.source_move_line_base_amount,
            600.0,
        )

        self._assert_float_equal(
            analytic_line_a_line_1.source_move_base_amount,
            1000.0,
        )

        self._assert_float_equal(
            analytic_line_a_line_1.source_move_total_analytic_percentage,
            30.0,
        )

    def test_source_move_total_percentage_uses_line_base_not_analytic_amount(self):
        invoice = self._create_invoice()

        analytic_lines = self.env["account.analytic.line"].search(
            [
                ("move_line_id.move_id", "=", invoice.id),
            ]
        )
        self.assertTrue(analytic_lines)

        invoice_line_2 = invoice.invoice_line_ids.filtered(
            lambda line: line.price_subtotal == 400.0
        )
        self.assertEqual(len(invoice_line_2), 1)

        analytic_line = analytic_lines.filtered(
            lambda line: line.move_line_id == invoice_line_2
        )
        self.assertEqual(len(analytic_line), 1)

        self._assert_float_equal(
            analytic_line.analytic_percentage,
            100.0,
        )

        self._assert_float_equal(
            analytic_line.source_move_line_base_amount,
            400.0,
        )

        self._assert_float_equal(
            analytic_line.source_move_base_amount,
            1000.0,
        )

        self._assert_float_equal(
            analytic_line.source_move_total_analytic_percentage,
            40.0,
        )

    def test_prepare_analytic_distribution_line_adds_source_move_info(self):
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Line 1",
                            "quantity": 1.0,
                            "price_unit": 250.0,
                            "account_id": self.income_account.id,
                            "analytic_distribution": {
                                str(self.analytic_account_a.id): 25.0,
                            },
                        },
                    ),
                ],
            }
        )

        invoice_line = invoice.invoice_line_ids
        self.assertEqual(len(invoice_line), 1)

        vals = invoice_line._prepare_analytic_distribution_line(
            25.0,
            str(self.analytic_account_a.id),
            {},
        )

        self.assertIn("source_move_currency_id", vals)
        self.assertIn("analytic_percentage", vals)
        self.assertIn("source_move_line_base_amount", vals)
        self.assertIn("source_move_base_amount", vals)
        self.assertIn("source_move_total_analytic_percentage", vals)

        self.assertEqual(vals["source_move_currency_id"], invoice.currency_id.id)

        self._assert_float_equal(
            vals["analytic_percentage"],
            25.0,
        )
        self._assert_float_equal(
            vals["source_move_line_base_amount"],
            250.0,
        )
        self._assert_float_equal(
            vals["source_move_base_amount"],
            250.0,
        )
        self._assert_float_equal(
            vals["source_move_total_analytic_percentage"],
            25.0,
        )

    def test_changing_analytic_distribution_recreates_lines_with_source_move_info(self):
        invoice = self._create_invoice()

        invoice_line_2 = invoice.invoice_line_ids.filtered(
            lambda line: line.price_subtotal == 400.0
        )
        self.assertEqual(len(invoice_line_2), 1)

        old_analytic_lines = self.env["account.analytic.line"].search(
            [
                ("move_line_id", "=", invoice_line_2.id),
            ]
        )
        self.assertEqual(len(old_analytic_lines), 1)
        old_analytic_line_ids = old_analytic_lines.ids

        invoice_line_2.write(
            {
                "analytic_distribution": {
                    str(self.analytic_account_b.id): 100.0,
                }
            }
        )

        new_analytic_lines = self.env["account.analytic.line"].search(
            [
                ("move_line_id", "=", invoice_line_2.id),
            ]
        )
        self.assertEqual(len(new_analytic_lines), 1)

        self.assertNotEqual(old_analytic_line_ids, new_analytic_lines.ids)

        self.assertTrue(
            self._analytic_line_has_account(
                new_analytic_lines,
                self.analytic_account_b,
            )
        )

        self._assert_float_equal(
            new_analytic_lines.analytic_percentage,
            100.0,
        )
        self._assert_float_equal(
            new_analytic_lines.source_move_line_base_amount,
            400.0,
        )
        self._assert_float_equal(
            new_analytic_lines.source_move_base_amount,
            1000.0,
        )
        self._assert_float_equal(
            new_analytic_lines.source_move_total_analytic_percentage,
            40.0,
        )

    def test_sql_backfill_matches_generated_values(self):
        invoice = self._create_invoice()

        analytic_lines = self.env["account.analytic.line"].search(
            [
                ("move_line_id.move_id", "=", invoice.id),
            ],
            order="id",
        )
        self.assertTrue(analytic_lines)

        expected_by_line = {
            line.id: {
                "source_move_currency_id": line.source_move_currency_id.id,
                "analytic_percentage": line.analytic_percentage,
                "source_move_line_base_amount": line.source_move_line_base_amount,
                "source_move_base_amount": line.source_move_base_amount,
                "source_move_total_analytic_percentage": (
                    line.source_move_total_analytic_percentage
                ),
            }
            for line in analytic_lines
        }

        analytic_lines.write(
            {
                "source_move_currency_id": False,
                "analytic_percentage": 0.0,
                "source_move_line_base_amount": 0.0,
                "source_move_base_amount": 0.0,
                "source_move_total_analytic_percentage": 0.0,
            }
        )
        self.env.flush_all()

        _sql_backfill_source_move_currency_id(self.env.cr)
        _sql_backfill_source_move_amounts(self.env.cr)
        _sql_backfill_analytic_percentage(
            self.env.cr,
            self._get_analytic_account_column_names_for_sql_hook(),
        )
        _sql_backfill_source_move_total_analytic_percentage(self.env.cr)

        analytic_line_ids = analytic_lines.ids

        self.env.invalidate_all()

        analytic_lines = self.env["account.analytic.line"].search(
            [
                ("id", "in", analytic_line_ids),
            ],
            order="id",
        )

        for line in analytic_lines:
            expected = expected_by_line[line.id]

            self.assertEqual(
                line.source_move_currency_id.id,
                expected["source_move_currency_id"],
            )

            self._assert_float_equal(
                line.analytic_percentage,
                expected["analytic_percentage"],
            )

            self._assert_float_equal(
                line.source_move_line_base_amount,
                expected["source_move_line_base_amount"],
            )

            self._assert_float_equal(
                line.source_move_base_amount,
                expected["source_move_base_amount"],
            )

            self._assert_float_equal(
                line.source_move_total_analytic_percentage,
                expected["source_move_total_analytic_percentage"],
            )
