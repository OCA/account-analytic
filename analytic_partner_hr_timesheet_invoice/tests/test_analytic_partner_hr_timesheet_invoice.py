# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import fields


class TestAnalyticPartnerHrTimesheetInvoice(common.TransactionCase):

    def setUp(self):
        super(TestAnalyticPartnerHrTimesheetInvoice, self).setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.other_partner = self.env.ref('base.res_partner_3')
        self.analytic_account = self.env['account.analytic.account'].create(
            {'name': 'Test Analytic Account',
             'state': 'draft',
             'partner_id': self.partner.id,
             'pricelist_id': self.env.ref('product.list0').id,
             'to_invoice': self.env.ref(
                 'hr_timesheet_invoice.timesheet_invoice_factor1').id,
             'type': 'normal'}
        )
        self.analytic_line_model = self.env['account.analytic.line']
        self.analytic_line_1 = self.analytic_line_model.create(
            {'name': 'Test for other partner',
             'account_id': self.analytic_account.id,
             'unit_amount': 1.0,
             'amount': 100.0,
             'date': fields.Date.today(),
             'general_account_id': self.env.ref('account.a_recv').id,
             'journal_id': self.env.ref('account.analytic_journal_sale').id,
             'to_invoice': self.analytic_account.to_invoice.id,
             'other_partner_id': self.other_partner.id})
        self.analytic_line_2 = self.analytic_line_model.create(
            {'name': 'Test for account partner',
             'account_id': self.analytic_account.id,
             'unit_amount': 1.0,
             'amount': 200.0,
             'date': fields.Date.today(),
             'general_account_id': self.env.ref('account.a_recv').id,
             'journal_id': self.env.ref('account.analytic_journal_sale').id,
             'to_invoice': self.analytic_account.to_invoice.id})

    def test_invoices_split_by_partner(self):
        lines = self.analytic_line_1 + self.analytic_line_2
        invoices = lines.invoice_cost_create()
        self.assertEqual(len(invoices), 2, "Invoices has not been split")

    def test_partner_invoice_1(self):
        invoice_id = self.analytic_line_1.invoice_cost_create()[0]
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.partner_id, self.other_partner)

    def test_partner_invoice_2(self):
        invoice_id = self.analytic_line_2.invoice_cost_create()[0]
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.partner_id, self.partner)
