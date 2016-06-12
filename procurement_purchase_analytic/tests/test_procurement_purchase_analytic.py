# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestProcurementPurchaseAnalytic(TransactionCase):
    """ Use case : Prepare some data for current test case """
    def setUp(self):
        super(TestProcurementPurchaseAnalytic, self).setUp()

        self.product = self.env.ref('product.product_product_8')
        self.partner = self.env.ref('base.res_partner_2')
        self.analytic_account = self.env['account.analytic.account'].create({
            'name': 'Test Analytic Account',
            'type': 'contract',
        })
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'project_id': self.analytic_account.id,
        })
        self.sale_order_line = self.sale_order_line.create(
            {'product_id': self.product.id,
             'product_uos_qty': 1,
             'price_unit': self.product.list_price,
             'order_id': self.sale_order.id,
             'name': self.product.name})

    def test_sale_to_procurement(self):
        # Confirm the sale order
        self.sale_order.action_button_confirm()

        # Search procurement generate by sale order
        procurement = self.env['procurement.order'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertTrue(procurement)

        # Search purchase order line generate by procurement run
        pol = self.env['purchase.order.line'].search(
            [('account_analytic_id', '=', self.analytic_account.id)])
        self.assertTrue(pol)
