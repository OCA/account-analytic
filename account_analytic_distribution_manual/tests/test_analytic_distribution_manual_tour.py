# Copyright 2024 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import RecordCapturer, new_test_user, tagged
from odoo.tests.common import HttpCase, users

from odoo.addons.account_analytic_distribution_manual.tests.common import (
    DistributionManualCommon,
)


@tagged("post_install", "-at_install")
class TestAnalyticDistributionManual(DistributionManualCommon, HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        new_test_user(
            cls.env,
            login="analytic-manual-distribution-user",
            groups="analytic.group_analytic_accounting,account.group_account_invoice",
        )

    @users("analytic-manual-distribution-user")
    def test_manual_distribution_tour(self):
        with RecordCapturer(
            self.env["account.move"], [("move_type", "=", "out_invoice")]
        ) as capt:
            self.start_tour(
                "/web",
                "account_analytic_distribution_manual",
                login="analytic-manual-distribution-user",
            )
        invoice = capt.records
        self.assertEqual(invoice.partner_id, self.partner_a)
        self.assertEqual(len(invoice.invoice_line_ids.analytic_line_ids), 2)
        analytic_line1 = invoice.invoice_line_ids.analytic_line_ids.filtered(
            lambda x: x.account_id == self.analytic_account_a1
        )
        self.assertEqual(analytic_line1.amount, 40)
        analytic_line2 = invoice.invoice_line_ids.analytic_line_ids.filtered(
            lambda x: x.account_id == self.analytic_account_a2
        )
        self.assertEqual(analytic_line2.amount, 60)
