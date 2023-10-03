# Copyright 2023 ForgeFlow S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestInvoiceTaxes(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.test_analytic_account1 = cls.env["account.analytic.account"].create(
            {"name": "test_analytic_account 1"}
        )
        cls.test_analytic_account2 = cls.env["account.analytic.account"].create(
            {"name": "test_analytic_account 2"}
        )

    def _create_invoice(self, analytic_per_line):
        invoice_form = Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        )
        invoice_form.partner_id = self.partner_a
        invoice_form.invoice_payment_term_id = self.env.ref(
            "account.account_payment_term_30days"
        )
        for product, analytic_account in analytic_per_line:
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.product_id = product
                if analytic_account:
                    line_form.analytic_account_id = analytic_account
                line_form.save()
        invoice = invoice_form.save()
        return invoice

    def test_01_one_analytic_per_receivable_line(self):
        # Distribute receivable by analytic account
        invoice = self._create_invoice(
            [
                (self.product_a, self.test_analytic_account1),
                (self.product_b, self.test_analytic_account2),
                (self.product_a, False),
            ]
        )
        ap_ar_lines = invoice.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        analytic_model = self.env["account.analytic.account"]
        self.assertEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == self.test_analytic_account1
            ).balance,
            2000.0,
        )
        self.assertEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == self.test_analytic_account2
            ).balance,
            400.0,
        )
        # tax line included in the receivable line wo analytic account
        self.assertEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == analytic_model
            ).balance,
            2720.0,
        )
