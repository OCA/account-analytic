# Copyright 2024 APSL-Nagarro - Miquel Alzanillas
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.tests import Form, tagged
from odoo.tests.common import users

from .common import TestAccountAnalyticTagBase


@tagged("post_install", "-at_install")
class TestAccountAnalyticTag(TestAccountAnalyticTagBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        invoice_form = Form(
            cls.env["account.move"]
            .with_user(cls.user)
            .with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = cls.partner_a
        # Add line and default analytic tag with spreadation enabled
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product_a
            line_form.analytic_tag_ids.add(cls.account_analytic_tag_spread_default)
        # Add line and analytic tag with spreadation enabled and exclusion
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product_b
            line_form.analytic_tag_ids.add(
                cls.account_analytic_tag_spread_with_exclusion
            )
        # Add line and analytic tag with spreadation enabled and inclusion
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product_c
            line_form.analytic_tag_ids.add(
                cls.account_analytic_tag_spread_with_inclusion
            )

        cls.invoice = invoice_form.save()
        cls.line_a = cls.invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == cls.product_a
        )
        cls.line_b = cls.invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == cls.product_b
        )
        cls.line_c = cls.invoice.invoice_line_ids.filtered(
            lambda x: x.product_id == cls.product_c
        )

    @users("test-analytic-tag-user")
    def test_spread_by_tag_default_01(self):
        # Check default tag configuration spreading without inclusions or exclusions
        # 3 analytic lines of -333,33$ are expected to be created
        # (1000$ / 3 Analytic Accounts)
        self.invoice.action_post()
        analytic_lines = self.env["account.analytic.line"].search(
            [("move_line_id", "=", self.line_a.id)]
        )
        self.assertRecordValues(
            analytic_lines,
            [
                {
                    "amount": -333.333333,
                    "account_id": self.analytic_account_c.id,
                },
                {
                    "amount": -333.333333,
                    "account_id": self.analytic_account_b.id,
                },
                {
                    "amount": -333.333333,
                    "account_id": self.analytic_account_a.id,
                },
            ],
        )

    @users("test-analytic-tag-user")
    def test_spread_by_tag_with_exclusion_02(self):
        # Check if tag configuration spreading with
        # EXCLUSION filter for 1 analytic account
        # Expected result: 2 analytic line of -500$ are expected to be created
        # (500$ / 2 Analytic Accounts)
        self.invoice.action_post()
        analytic_lines = self.env["account.analytic.line"].search(
            [("move_line_id", "=", self.line_b.id)]
        )

        self.assertRecordValues(
            analytic_lines,
            [
                {
                    "amount": -500.0,
                    "account_id": self.analytic_account_c.id,
                },
                {
                    "amount": -500.0,
                    "account_id": self.analytic_account_b.id,
                },
            ],
        )

    @users("test-analytic-tag-user")
    def test_spread_by_tag_account_inclusion_03(self):
        # Check if tag configuration spreading
        # with INCLUSION filter for 1 analytic account
        # Expected result: 1 analytic line of -1000$
        # are expected to be created (1000$ / 1 Analytic Accounts)
        self.invoice.action_post()
        analytic_lines = self.env["account.analytic.line"].search(
            [("move_line_id", "=", self.line_c.id)]
        )
        self.assertRecordValues(
            analytic_lines,
            [
                {
                    "amount": -1000,
                    "account_id": self.analytic_account_a.id,
                }
            ],
        )

    @users("test-analytic-tag-user")
    def test_analytic_lines_deletion_after_invoice_cancellation(self):
        # Post the invoice
        self.invoice.action_post()

        # Check that analytic lines have been created
        analytic_lines = self.env["account.analytic.line"].search(
            [("move_line_id", "in", self.invoice.invoice_line_ids.ids)]
        )
        self.assertTrue(analytic_lines)

        # Cancel the invoice
        self.invoice.button_cancel()

        # Check that analytic lines have been deleted
        analytic_lines_after = self.env["account.analytic.line"].search(
            [("move_line_id", "in", self.invoice.invoice_line_ids.ids)]
        )
        self.assertFalse(analytic_lines_after)

    @users("test-analytic-tag-user")
    def test_analytic_lines_inherit_tags_from_invoice_lines(self):
        # Post the invoice
        self.invoice.action_post()

        # Check that analytic lines have been created
        analytic_lines = self.env["account.analytic.line"].search(
            [("move_line_id", "in", self.invoice.invoice_line_ids.ids)]
        )
        self.assertTrue(analytic_lines)

        # Check that each analytic line has the
        # same tags as its corresponding invoice line
        for line in analytic_lines:
            invoice_line = self.invoice.invoice_line_ids.filtered(
                lambda x, y=line.move_line_id: x.id == y.id
            )
            self.assertEqual(line.tag_ids, invoice_line.analytic_tag_ids)
