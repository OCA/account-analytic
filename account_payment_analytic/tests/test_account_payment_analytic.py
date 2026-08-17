from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountPaymentAnalytic(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Payment Plan"}
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Payment Analytic", "plan_id": cls.analytic_plan.id}
        )
        cls.bank_journal = cls.company_data["default_journal_bank"]

    def _create_payment(self, analytic_distribution=None):
        return self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_a.id,
                "amount": 100.0,
                "journal_id": self.bank_journal.id,
                "analytic_distribution": analytic_distribution,
            }
        )

    def test_distribution_pushed_to_counterpart_line(self):
        payment = self._create_payment({str(self.analytic_account.id): 100})
        payment.action_post()
        counterpart_lines = payment.move_id.line_ids.filtered(
            lambda line: line.account_id == payment.destination_account_id
        )
        self.assertTrue(counterpart_lines)
        for line in counterpart_lines:
            self.assertEqual(line.analytic_distribution, payment.analytic_distribution)
        other_lines = payment.move_id.line_ids - counterpart_lines
        self.assertFalse(other_lines.filtered("analytic_distribution"))

    def test_no_distribution_leaves_lines_empty(self):
        payment = self._create_payment()
        payment.action_post()
        self.assertFalse(payment.move_id.line_ids.filtered("analytic_distribution"))

    def test_distribution_from_register_wizard(self):
        invoice = self.init_invoice(
            "out_invoice", partner=self.partner_a, amounts=[100.0], post=True
        )
        distribution = {str(self.analytic_account.id): 100}
        wizard = (
            self.env["account.payment.register"]
            .with_context(active_model="account.move", active_ids=invoice.ids)
            .create({"analytic_distribution": distribution})
        )
        payment = wizard._create_payments()
        self.assertEqual(payment.analytic_distribution, distribution)
        counterpart_lines = payment.move_id.line_ids.filtered(
            lambda line: line.account_id == payment.destination_account_id
        )
        self.assertTrue(counterpart_lines)
        for line in counterpart_lines:
            self.assertEqual(line.analytic_distribution, payment.analytic_distribution)
