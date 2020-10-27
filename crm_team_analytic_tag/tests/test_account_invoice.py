# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.analytic_tag1 = self.env['account.analytic.tag'].create(
            {'name': 'test analytic_tag1'}
        )
        self.analytic_tag2 = self.env['account.analytic.tag'].create(
            {'name': 'test analytic_tag2'}
        )
        self.partner = self.env['res.partner'].create({'name': 'Test partner'})
        self.journal = self.env['account.journal'].create(
            {
                'name': 'Test journal',
                'code': 'TEST',
                'type': 'general',
                'update_posted': True,
            }
        )
        self.account_type = self.env['account.account.type'].create(
            {'name': 'Test account type', 'type': 'other'}
        )
        self.account = self.env['account.account'].create(
            {
                'name': 'Test account',
                'code': 'TEST',
                'user_type_id': self.account_type.id,
            }
        )
        self.invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.partner.id,
                'journal_id': self.journal.id,
                'type': 'out_invoice',
                'invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'name': 'Test line',
                            'quantity': 1,
                            'price_unit': 50,
                            'account_id': self.account.id,
                        },
                    )
                ],
            }
        )
        self.invoice_line = self.invoice.invoice_line_ids[0]
        self.team = self.env['crm.team'].create(
            {
                'name': 'test team',
                'analytic_tag_ids': [(4, self.analytic_tag1.id)],
            }
        )

    def test_onchange_team_id(self):
        self.invoice.team_id = self.team
        self.invoice._onchange_team_analytic_tags()
        self.assertEqual(
            self.invoice_line.analytic_tag_ids,
            self.analytic_tag1,
        )

    def test_create_invoice(self):
        self.invoice.team_id = self.team
        create_data = {
            'name': 'Test Line',
            'quantity': 1,
            'price_unit': 1,
            'account_id': self.account.id,
            'invoice_id': self.invoice.id,
        }
        invoice_line = self.env['account.invoice.line'].create(create_data)
        self.assertEqual(
            invoice_line.analytic_tag_ids,
            self.analytic_tag1,
        )

    def test_create_invoice_1(self):
        invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.partner.id,
                'journal_id': self.journal.id,
                'type': 'out_invoice',
                'team_id': self.team.id,
                'invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'name': 'Test line',
                            'quantity': 1,
                            'price_unit': 50,
                            'account_id': self.account.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            invoice.invoice_line_ids.analytic_tag_ids,
            self.analytic_tag1,
        )

    def test_create_invoice_2(self):
        invoice = self.env['account.invoice'].create(
            {
                'partner_id': self.partner.id,
                'journal_id': self.journal.id,
                'type': 'out_invoice',
                'team_id': self.team.id,
                'invoice_line_ids': [
                    (
                        0,
                        0,
                        {
                            'name': 'Test line',
                            'quantity': 1,
                            'price_unit': 50,
                            'account_id': self.account.id,
                            'analytic_tag_ids': [(4, self.analytic_tag2.id)],
                        },
                    )
                ],
            }
        )
        self.assertEqual(
            invoice.invoice_line_ids.analytic_tag_ids,
            self.analytic_tag1 | self.analytic_tag2,
        )
