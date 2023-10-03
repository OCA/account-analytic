# Copyright 2024 ForgeFlow S.L.
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
        cls.tax_15_s = cls.company_data["default_tax_sale"]

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
        invoice = invoice_form.save()
        return invoice

    def test_01_one_analytic_per_receivable_line(self):
        # Distribute receivable by analytic account
        invoice = self._create_invoice(
            [
                (self.product_a, self.test_analytic_account1),  # product a $1000
                (self.product_b, self.test_analytic_account2),  # product b $200
                (self.product_a, False),
            ]
        )
        ap_ar_lines = invoice.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        analytic_model = self.env["account.analytic.account"]
        # expected balances (default tax 15%) in product A (2 15 % taxes in product b):
        # if product sales value $ 1000 then 1000 + 1000*0.15 = $1150
        # if product sales value $ 200 then 200+ 200*0.15 + 200*0.15 = $260
        self.assertAlmostEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == analytic_model
            ).balance,
            1150.0,
            places=2,
        )
        self.assertAlmostEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == self.test_analytic_account1
            ).balance,
            1150.0,
            places=2,
        )
        self.assertAlmostEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == self.test_analytic_account2
            ).balance,
            260.0,
            places=2,
        )

    def test_02_no_split_when_same_analytic_line(self):
        # Same analytic account with same taxes: no split
        # same taxes in both invoice lines to ensure one AR line only
        self.product_b.write({"taxes_id": [(6, 0, (self.tax_sale_a).ids)]})
        invoice = self._create_invoice(
            [
                (self.product_a, self.test_analytic_account2),  # product a $1000
                (self.product_b, self.test_analytic_account2),  # product b $200
            ]
        )
        ap_ar_lines = invoice.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in ("receivable", "payable")
        )
        # only one line
        self.assertEqual(len(ap_ar_lines), 1)
        # check the balance, all balance for the same analytic account
        self.assertEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == self.test_analytic_account1
            ).balance,
            0.0,
        )
        # tax line in the AA line
        tax_balance = sum(
            invoice.line_ids.filtered(lambda line: "Tax" in line.name).mapped("balance")
        )
        self.assertEqual(
            ap_ar_lines.filtered(
                lambda l: l.analytic_account_id == self.test_analytic_account2
            ).balance,
            1200 + abs(tax_balance),
        )
