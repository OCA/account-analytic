# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestAnalyticPartner(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test journal", "code": "TEST", "type": "sale"}
        )
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test account type", "type": "other", "internal_group": "equity"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
            }
        )
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "Test Analytic Account"}
        )
        cls.account_move = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "journal_id": cls.journal.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "account_id": cls.account.id,
                            "analytic_account_id": cls.analytic_account.id,
                            "quantity": 10.0,
                            "price_unit": 50.0,
                        },
                    )
                ],
            }
        )

    def test_flow(self):
        self.account_move.action_post()
        analytic_lines = self.account_move.mapped("line_ids.analytic_line_ids")
        for analytic_line in analytic_lines:
            self.assertEqual(
                analytic_line.other_partner_id,
                self.account_move.partner_id.commercial_partner_id,
                """Invoice partner has not been propagated
                   to the analytic line""",
            )
