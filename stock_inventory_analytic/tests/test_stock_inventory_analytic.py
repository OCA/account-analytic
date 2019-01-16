# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestInventoryAnalytic(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestInventoryAnalytic, cls).setUpClass()

        # MODELS
        cls.product_product_model = cls.env['product.product']
        cls.product_category_model = cls.env['product.category']
        cls.wizard_model = cls.env['stock.change.product.qty']

        # INSTANCES
        cls.category = cls.product_category_model.create({
            'name': 'Physical (test)',
            'property_cost_method': 'standard',
            'property_valuation': 'real_time',
        })
        cls.analytic_account = cls.env.ref(
            'analytic.analytic_agrolait')

    def _create_product(self, name):
        return self.product_product_model.create({
            'name': name,
            'categ_id': self.category.id,
            'type': 'product',
            'standard_price': 100, })

    def _product_change_qty(self, product, new_qty,
                            analytic_account_id=None):
        values = {
            'product_id': product.id,
            'new_quantity': new_qty,
        }
        if analytic_account_id:
            values.update({'analytic_account_id': analytic_account_id.id})
        wizard = self.wizard_model.create(values)
        wizard.change_product_qty()

    def test_product_change_qty_analytic(self):
        product = self._create_product('product_product')

        analytic_lines_before = self.env['account.analytic.line'].search(
            [('product_id', '=', product.id),
             ('account_id', '=', self.analytic_account.id)])

        self._product_change_qty(product, 10, self.analytic_account)

        analytic_lines_after = self.env['account.analytic.line'].search(
            [('product_id', '=', product.id),
             ('account_id', '=', self.analytic_account.id)])

        self.assertNotEqual(analytic_lines_before, analytic_lines_after)

        analytic_line_created = analytic_lines_after - analytic_lines_before

        self.assertEqual(analytic_line_created.unit_amount, 10)
        self.assertEqual(analytic_line_created.amount,
                         product.standard_price * 10)
