# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command
from odoo.tests import Form, TransactionCase


class TestAccountMoveAnalytic(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id |= cls.env.ref("analytic.group_analytic_accounting")
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 100.0,
            }
        )
        analytic_plan = cls.env["account.analytic.plan"].create({"name": "Plan Test"})
        cls.analytic_account = cls.env["account.analytic.account"].create(
            {"name": "manual", "plan_id": analytic_plan.id}
        )
        cls.analytic_distribution = {str(cls.analytic_account.id): 100}
        cls.analytic_distribution2 = {str(cls.analytic_account.id): 50}

    def _create_invoice(self, move_type="out_invoice"):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.partner.id,
            }
        )

    def _add_invoice_line(self, move, product=None):
        if not product:
            product = self.product
        move.invoice_line_ids = [
            Command.create(
                {
                    "product_id": product.id,
                    "quantity": 1,
                    "price_unit": 100.0,
                }
            )
        ]

    def test_analytic_distribution_propagates_to_lines(self):
        invoice = self._create_invoice()
        self._add_invoice_line(invoice)
        invoice.analytic_distribution = self.analytic_distribution
        self.assertEqual(invoice.analytic_distribution, self.analytic_distribution)
        self.assertEqual(
            invoice.invoice_line_ids[0].analytic_distribution,
            self.analytic_distribution,
        )

    def test_analytic_distribution_computed_from_lines(self):
        invoice = self._create_invoice()
        self._add_invoice_line(invoice)
        invoice.invoice_line_ids[0].analytic_distribution = self.analytic_distribution
        self.assertEqual(invoice.analytic_distribution, self.analytic_distribution)

    def test_analytic_distribution_different_lines(self):
        invoice = self._create_invoice()
        invoice.invoice_line_ids = [
            Command.create(
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "price_unit": 100.0,
                    "analytic_distribution": self.analytic_distribution,
                }
            ),
            Command.create(
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "price_unit": 200.0,
                    "analytic_distribution": self.analytic_distribution2,
                }
            ),
        ]
        self.assertFalse(invoice.analytic_distribution)

    def test_sections_and_notes_excluded(self):
        invoice = self._create_invoice()
        invoice.invoice_line_ids = [
            Command.create(
                {
                    "display_type": "line_section",
                    "name": "Section",
                }
            ),
            Command.create(
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "price_unit": 100.0,
                    "analytic_distribution": self.analytic_distribution,
                }
            ),
            Command.create(
                {
                    "display_type": "line_note",
                    "name": "Note",
                }
            ),
        ]
        self.assertEqual(invoice.analytic_distribution, self.analytic_distribution)

    def test_analytic_distribution_with_form(self):
        with Form(
            self.env["account.move"].with_context(default_move_type="out_invoice")
        ) as invoice_form:
            invoice_form.partner_id = self.partner
            invoice_form.analytic_distribution = self.analytic_distribution
            with invoice_form.invoice_line_ids.new() as line:
                line.product_id = self.product
                line.quantity = 1
                line.price_unit = 100.0
        invoice = invoice_form.record
        self.assertEqual(invoice.analytic_distribution, self.analytic_distribution)
        self.assertEqual(
            invoice.invoice_line_ids.filtered(
                lambda ln: ln.display_type not in ("line_section", "line_note")
            )[0].analytic_distribution,
            self.analytic_distribution,
        )

    def test_vendor_bill_analytic_distribution(self):
        bill = self._create_invoice(move_type="in_invoice")
        self._add_invoice_line(bill)
        bill.analytic_distribution = self.analytic_distribution
        self.assertEqual(bill.analytic_distribution, self.analytic_distribution)
        self.assertEqual(
            bill.invoice_line_ids[0].analytic_distribution,
            self.analytic_distribution,
        )

    def test_journal_entry_no_analytic_distribution(self):
        journal = self.env["account.journal"].search(
            [("type", "=", "general")], limit=1
        )
        account = self.env["account.account"].search([], limit=1)
        entry = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": journal.id,
                "line_ids": [
                    Command.create(
                        {
                            "account_id": account.id,
                            "debit": 100.0,
                            "analytic_distribution": self.analytic_distribution,
                        }
                    ),
                    Command.create(
                        {
                            "account_id": account.id,
                            "credit": 100.0,
                        }
                    ),
                ],
            }
        )
        self.assertFalse(entry.analytic_distribution)
