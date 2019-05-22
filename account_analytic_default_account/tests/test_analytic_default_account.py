# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common
import time
import mock

MOCK_PATH = 'odoo.addons.account_analytic_default_account'


class TestAnalyticDefaultAccount(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref('base.main_company')
        cls.account_analytic_default_model = \
            cls.env['account.analytic.default']
        cls.analytic_account_model = cls.env['account.analytic.account']
        cls.invoice_model = cls.env['account.invoice']
        cls.invoice_line_model = cls.env['account.invoice.line']
        cls.move_obj = cls.env['account.move']
        cls.move_line_obj = cls.env['account.move.line']

        cls.partner_agrolait = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_product_4")
        cls.account_receivable = cls.env['account.account'].create({
            'code': "X1035",
            'name': "Income",
            'user_type_id':
                cls.env.ref('account.data_account_type_receivable').id,
            'reconcile': True,
        })
        cls.partner_agrolait.property_account_receivable_id =\
            cls.account_receivable.id
        cls.account_sales = cls.env['account.account'].create({
            'code': "X1020",
            'name': "Product Sales - (test)",
            'user_type_id': cls.env.ref('account.data_account_type_revenue').id
        })

        cls.sales_journal = cls.env['account.journal'].create({
            'name': "Sales Journal - (test)",
            'code': "TSAJ",
            'type': "sale",
            'refund_sequence': True,
            'default_debit_account_id': cls.account_sales.id,
            'default_credit_account_id': cls.account_sales.id,
        })

        cls.analytic_account_1 = cls.analytic_account_model.create(
            {'name': 'test 1'})
        cls.analytic_account_2 = cls.analytic_account_model.create(
            {'name': 'test 2'})
        cls.analytic_account_3 = cls.analytic_account_model.create(
            {'name': 'test 3'})
        cls.analytic_account_4 = cls.analytic_account_model.create(
            {'name': 'test 4'})
        cls.analytic_account_5 = cls.analytic_account_model.create(
            {'name': 'test 5'})
        cls.analytic_account_6 = cls.analytic_account_model.create(
            {'name': 'test 6'})

        cls.account_analytic_default_model.create({
            'product_id': cls.product.id,
            'analytic_id': cls.analytic_account_1.id
        })
        cls.account_analytic_default_model.create({
            'partner_id': cls.partner_agrolait.id,
            'analytic_id': cls.analytic_account_2.id
        })
        cls.account_analytic_default_model.create({
            'product_id': cls.product.id,
            'account_id': cls.account_sales.id,
            'analytic_id': cls.analytic_account_3.id
        })
        cls.account_analytic_default_model.create({
            'account_id': cls.account_sales.id,
            'analytic_id': cls.analytic_account_4.id
        })

    def create_invoice(self, amount=100, inv_type='out_invoice'):
        """ Returns an open invoice """
        invoice = self.invoice_model.create({
            'partner_id': self.partner_agrolait.id,
            'reference_type': 'none',
            'name': (inv_type == 'out_invoice' and 'invoice to client' or
                     'invoice to supplier'),
            'account_id': self.account_receivable.id,
            'type': inv_type,
            'date_invoice': time.strftime('%Y') + '-06-26',
        })
        self.invoice_line_model.create({
            'product_id': self.product.id,
            'quantity': 1,
            'price_unit': amount,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': self.account_sales.id
        })
        invoice.action_invoice_open()
        return invoice

    def create_move(self, amount=100, product_id=None, partner_id=None,
                    date=None):
        ml_obj = self.move_line_obj.with_context(check_move_validity=False)
        if not date:
            date = time.strftime('%Y') + '-07-25',
        move_vals = {
            'name': '/',
            'journal_id': self.sales_journal.id,
            'date': date,
            'partner_id': partner_id,
        }
        move = self.move_obj.create(move_vals)
        move_line_1 = ml_obj.create({
            'move_id': move.id,
            'name': '/',
            'debit': 0,
            'credit': amount,
            'account_id': self.account_sales.id,
            'product_id': product_id,
            'partner_id': partner_id,
        })
        move_line_2 = ml_obj.create({
            'move_id': move.id,
            'name': '/',
            'debit': amount,
            'credit': 0,
            'account_id': self.account_receivable.id,
            'partner_id': partner_id,
        })
        return move, move_line_1, move_line_2

    def test_account_analytic_default_get_account(self):
        rec = self.account_analytic_default_model.account_get(
            account_id=self.account_sales.id
        )
        self.assertEqual(self.analytic_account_4.id, rec.analytic_id.id)

        rec = self.account_analytic_default_model.account_get(
            account_id=self.account_receivable.id
        )
        self.assertFalse(rec.id)

    def test_account_analytic_default_invoice(self):
        invoice = self.create_invoice()
        self.assertFalse(invoice.invoice_line_ids[0].account_analytic_id.id)
        invoice.invoice_line_ids[0]._set_additional_fields(invoice)
        self.assertEqual(invoice.invoice_line_ids[0].account_analytic_id,
                         self.analytic_account_3)

    def test_account_analytic_default_account_move(self):
        move, move_line_1, move_line_2 = self.create_move()
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_4)
        self.assertFalse(move_line_2.analytic_account_id.id)

        # set company
        self.account_analytic_default_model.create({
            'account_id': self.account_sales.id,
            'analytic_id': self.analytic_account_1.id,
            'company_id': self.company.id,
            'product_id': self.product.id,
            'user_id': self.env.uid,
        })

        # still same aal as move line have no defined product
        move_line_1.analytic_account_id = ''
        move_line_1._onchange_account_id()
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_4)

        # but have a new one if product set
        move_line_1.analytic_account_id = ''
        move_line_1.product_id = self.product.id
        move_line_1._onchange_account_id()
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_1)

    def test_account_analytic_default_best_choice(self):
        # match on product
        move, move_line_1, _ = self.create_move(
            100, self.product.id,
        )
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_3)
        # set user
        self.account_analytic_default_model.create({
            'account_id': self.account_sales.id,
            'analytic_id': self.analytic_account_5.id,
            'product_id': self.product.id,
            'user_id': self.env.uid,
        })
        move, move_line_1, _ = self.create_move(
            100, self.product.id, self.partner_agrolait.id
        )
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_5)
        # set company
        self.account_analytic_default_model.create({
            'account_id': self.account_sales.id,
            'analytic_id': self.analytic_account_6.id,
            'company_id': self.company.id,
            'product_id': self.product.id,
            'user_id': self.env.uid,
        })
        move, move_line_1, _ = self.create_move(
            100, self.product.id, self.partner_agrolait.id
        )
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_6)
        # create account with time constrains
        self.account_analytic_default_model.create({
            'account_id': self.account_sales.id,
            'analytic_id': self.analytic_account_1.id,
            'company_id': self.company.id,
            'product_id': self.product.id,
            'user_id': self.env.uid,
            'date_start': '%s-07-01' % time.strftime('%Y'),
            'date_stop': '%s-07-31' % time.strftime('%Y'),
        })
        with mock.patch(
                MOCK_PATH + '.models.account_analytic_default_account.fields.'
                            'Date.today'
        ) as fnct:
            fnct.return_value = '%s-07-15' % time.strftime('%Y')
            move, move_line_1, _ = self.create_move(
                100, self.product.id, self.partner_agrolait.id
            )
            self.assertEqual(move_line_1.analytic_account_id,
                             self.analytic_account_1)

        # when period to use default account ends we get previous aal
        move, move_line_1, _ = self.create_move(
            100, self.product.id, self.partner_agrolait.id,
            '%s-08-15' % time.strftime('%Y')
        )
        self.assertEqual(move_line_1.analytic_account_id,
                         self.analytic_account_6)
