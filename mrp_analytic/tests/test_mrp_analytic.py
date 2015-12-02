# -*- coding: utf-8 -*-
# © 2015 Pedro M. Baeza - Antiun Ingeniería
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests import common


class TestMrpAnalytic(common.TransactionCase):

    def setUp(self):
        super(TestMrpAnalytic, self).setUp()
        self.analytic_account = self.env['account.analytic.account'].create(
            {'name': 'Analytic account test'})
        self.product = self.env['product.product'].create({'name': 'Test'})
        self.bom = self.env['mrp.bom'].create(
            {
                'product_id': self.product.id,
                'product_tmpl_id': self.product.product_tmpl_id.id,
            })
        self.production = self.env['mrp.production'].create(
            {
                'product_id': self.product.id,
                'analytic_account_id': self.analytic_account.id,
                'product_uom': self.product.uom_id.id,
            })

    def test_num_productions(self):
        self.assertEqual(self.analytic_account.num_productions, 1)
