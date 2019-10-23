# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from datetime import datetime


class TestPurchaseAnalytic(TransactionCase):

    def setUp(self):
        super(TestPurchaseAnalytic, self).setUp()
        self.project = self.env['account.analytic.account'].create({
            'name': 'Account Analytic for Tests',
        })

    def test_analytic_account(self):
        """ Create a purchase order with line
            Set analytic account on purchase
            Check analytic account on line is set
        """
        product_id = self.env.ref('product.product_product_9')
        po = self.env['purchase.order'].create(
            {'partner_id': self.env.ref('base.res_partner_12').id,
             'order_line': [
                 (0, 0, {
                     'name': product_id.name,
                     'product_id': product_id.id,
                     'product_qty': 1.0,
                     'product_uom': self.env.ref(
                         'uom.product_uom_unit').id,
                     'price_unit': 121.0,
                     'date_planned': datetime.today(),
                 })],
             })

        po.project_id = self.project.id
        self.assertEqual(po.project_id.id,
                         self.project.id)
        self.assertEqual(po.order_line.account_analytic_id.id,
                         self.project.id)

    def test_project_id(self):
        """ Create a purchase order without line
            Set analytic account on purchase
            Check analytic account is on purchase
        """
        po = self.env['purchase.order'].new(
            {'partner_id': self.env.ref('base.res_partner_12').id,
             'project_id': self.project.id
             })
        po._onchange_project_id()
        self.assertEqual(po.project_id.id,
                         self.project.id)
