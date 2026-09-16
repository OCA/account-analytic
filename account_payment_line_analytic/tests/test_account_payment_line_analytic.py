# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountPaymentLineAnalytic(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Bridge Plan"}
        )
        cls.analytic_account_a = cls.env["account.analytic.account"].create(
            {"name": "Bridge A", "plan_id": cls.analytic_plan.id}
        )
        cls.analytic_account_b = cls.env["account.analytic.account"].create(
            {"name": "Bridge B", "plan_id": cls.analytic_plan.id}
        )
        cls.bank_journal = cls.company_data["default_journal_bank"]

    def _create_payment(self, analytic_distribution=None, amount=100.0):
        return self.env["account.payment"].create(
            {
                "payment_type": "inbound",
                "partner_type": "customer",
                "partner_id": self.partner_a.id,
                "amount": amount,
                "journal_id": self.bank_journal.id,
                "analytic_distribution": analytic_distribution,
            }
        )

    def test_payment_distribution_propagated_to_line_and_move(self):
        """A proposed line inherits the payment distribution and, once posted,
        that distribution reaches its journal item."""
        self._create_invoice(post=True)
        payment = self._create_payment({str(self.analytic_account_a.id): 100})
        payment.action_propose_payment_distribution()
        line = payment.line_payment_counterpart_ids
        self.assertTrue(line)
        self.assertEqual(line.analytic_distribution, payment.analytic_distribution)
        payment.action_post()
        self.assertTrue(line.move_ids)
        self.assertEqual(
            line.move_ids.analytic_distribution, payment.analytic_distribution
        )

    def test_line_keeps_its_own_distribution(self):
        """A line with its own distribution is not overwritten by the payment."""
        self._create_invoice(post=True)
        payment = self._create_payment({str(self.analytic_account_a.id): 100})
        payment.action_propose_payment_distribution()
        line = payment.line_payment_counterpart_ids
        own_distribution = {str(self.analytic_account_b.id): 100}
        line.analytic_distribution = own_distribution
        self.assertEqual(line.analytic_distribution, own_distribution)

    def test_lines_without_payment_distribution_stay_empty(self):
        """Without a distribution on the payment, proposed lines stay empty."""
        self._create_invoice(post=True)
        payment = self._create_payment()
        payment.action_propose_payment_distribution()
        lines = payment.line_payment_counterpart_ids
        self.assertTrue(lines)
        self.assertFalse(lines.filtered("analytic_distribution"))
