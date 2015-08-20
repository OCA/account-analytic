# -*- coding: utf-8 -*-
# (c) 2015 Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
import openerp.tests.common as common
from openerp import workflow


class TestAnalyticPartner(common.TransactionCase):

    def setUp(self):
        super(TestAnalyticPartner, self).setUp()
        product = self.env.ref('product.product_product_5')
        self.analytic_account = self.env['account.analytic.account'].create(
            {'name': 'Test Analytic Account',
             'state': 'draft',
             'type': 'normal'}
        )
        self.invoice = self.env['account.invoice'].create(
            {'journal_id': self.env.ref('account.sales_journal').id,
             'partner_id': self.env.ref('base.res_partner_3').id,
             'account_id': self.env.ref('account.a_recv').id,
             'invoice_line': [
                 (0, 0, {'product_id': product.id,
                         'name': 'Test',
                         'account_analytic_id': self.analytic_account.id,
                         'quantity': 10.0,
                         })],
             })
        workflow.trg_validate(self.uid, 'account.invoice', self.invoice.id,
                              'invoice_open', self.cr)

    def test_partner_from_invoice(self):
        analytic_lines = self.invoice.move_id.mapped('line_id.analytic_lines')
        for analytic_line in analytic_lines:
            self.assertEqual(
                analytic_line.other_partner_id,
                self.invoice.partner_id.commercial_partner_id,
                'Invoice partner has not been propagated to the analytic line')
