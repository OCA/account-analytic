# Copyright 2015 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestPosAnalyticConfig(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aml_obj = cls.env['account.move.line']
        cls.inv_line_obj = cls.env['account.invoice.line']
        cls.main_config = cls.env.ref('point_of_sale.pos_config_main')
        cls.aa_01 = cls.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
        })
        cls.customer_01 = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.product_01 = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.aml_analytic_domain = [
            ('product_id', '=', cls.product_01.id),
            ('analytic_account_id', '=', cls.aa_01.id),
        ]
        cls.inv_analytic_domain = [
            ('product_id', '=', cls.product_01.id),
            ('account_analytic_id', '=', cls.aa_01.id),
        ]
        cls.main_config.account_analytic_id = cls.aa_01
        cls.session_01 = cls.env['pos.session'].create(
            {'config_id': cls.main_config.id})
        cls.session_01.action_pos_session_open()
        order_vals = {
            'session_id': cls.session_01.id,
            'partner_id': cls.customer_01.id,
            'lines': [(0, 0, {
                'product_id': cls.product_01.id,
                'qty': 1,
                'price_unit': 10.0,
                'price_subtotal': 10,
                'price_subtotal_incl': 10,
            })],
            'amount_total': 10.0,
            'amount_tax': 0.0,
            'amount_paid': 10.0,
            'amount_return': 0.0,
        }
        cls.order_01 = cls.env['pos.order'].create(order_vals)
        payment_data = {
            'amount': 10,
            'journal': cls.main_config.journal_ids[0].id,
            'partner_id': cls.order_01.partner_id.id,
        }
        cls.order_01.add_payment(payment_data)
        cls.order_01.action_pos_order_paid()

    def test_order_simple_receipt(self):
        """Simple ticket"""
        aml = self.aml_obj.search(self.aml_analytic_domain)
        # There aren't lines with the analytic account yet
        self.assertEqual(len(aml.ids), 0)
        self.session_01.action_pos_session_closing_control()
        self.session_01.action_pos_session_close()
        # There they are
        aml = self.aml_obj.search(self.aml_analytic_domain)
        self.assertEqual(len(aml.ids), 1)

    def test_order_invoice(self):
        """Ticket with invoice"""
        lines = self.inv_line_obj.search(self.inv_analytic_domain)
        self.order_01.action_pos_order_invoice()
        # There aren't lines with the analytic account yet
        self.assertEqual(len(lines.ids), 0)
        lines = self.inv_line_obj.search(self.inv_analytic_domain)
        # There they are
        self.assertEqual(len(lines.ids), 1)
