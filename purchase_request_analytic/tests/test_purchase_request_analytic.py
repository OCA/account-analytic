# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestPurchaseRequestAnalytic(TransactionCase):

    def setUp(self):
        super(TestPurchaseRequestAnalytic, self).setUp()
        self.anal_id = self.env['account.analytic.account'].create({
            'name': 'Account Analytic for Tests'
        })

    def test_analytic_account(self):
        """ Create a purchase order with line
            Set analytic account on purchase
            Check analytic account on line is set
        """
        product_id = self.env.ref('product.product_product_9')
        pr = self.env['purchase.request'].create(
            {'partner_id': self.env.ref('base.res_partner_12').id,
             'line_ids': [
                 (0, 0, {
                     'name': product_id.name,
                     'product_id': product_id.id,
                     'product_qty': 1.0,
                     'product_uom': self.env.ref(
                         'uom.product_uom_unit').id,
                 })],
             })

        pr.analytic_account_id = self.anal_id.id
        self.assertEqual(pr.analytic_account_id.id,
                         self.anal_id.id)
        self.assertEqual(pr.line_ids.analytic_account_id.id,
                         self.anal_id.id)

    def test_analytic(self):
        """ Create a purchase order without line
            Set analytic account on purchase
            Check analytic account is on purchase
        """
        pr = self.env['purchase.request'].new(
            {'partner_id': self.env.ref('base.res_partner_12').id,
             'analytic_account_id': self.anal_id.id
             })
        pr._onchange_analytic_account_id()
        self.assertEqual(pr.analytic_account_id.id,
                         self.anal_id.id)
