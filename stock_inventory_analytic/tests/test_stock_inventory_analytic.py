# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# Copyright 2019 brain-tec AG
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInventoryAnalytic(TransactionCase):

    def setUp(self):
        super(TestInventoryAnalytic, self).setUp()

        # MODELS
        self.product_product_model = self.env['product.product']
        self.product_category_model = self.env['product.category']
        self.wizard_model = self.env['stock.change.product.qty']

        # INSTANCES
        self.category = self.product_category_model.create({
            'name': 'Physical (test)',
            'property_cost_method': 'standard',
            'property_valuation': 'real_time',
        })
        self.analytic_account = self.env.ref(
            'analytic.analytic_agrolait')

        # Accounts for the product & product's category.
        account_group = self.env['account.group'].create({
            'name': 'Account Group (test)',
            'code_prefix': 'AGTest-',
        })
        user_type = self.env.ref('account.data_account_type_liquidity')
        self.account_account_70000 = self.env['account.account'].create({
            'code': '70000',
            'name': '70000 (test)',
            'group_id': account_group.id,
            'user_type_id': user_type.id,
        })
        self.account_account_70001 = self.env['account.account'].create({
            'code': '70001',
            'name': '70001 (test)',
            'group_id': account_group.id,
            'user_type_id': user_type.id,
        })

    def _create_product(self, name):
        self.category.property_stock_valuation_account_id = \
            self.account_account_70000.id
        return self.product_product_model.create({
            'name': name,
            'categ_id': self.category.id,
            'type': 'product',
            'standard_price': 100,
            'property_stock_account_input': self.account_account_70000.id,
            'property_stock_account_output': self.account_account_70001.id,
        })

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

        inventory_lines_before = self.env['stock.inventory.line'].search([
            ('product_id', '=', product.id),
            ('analytic_account_id', '=', self.analytic_account.id),
        ])
        analytic_lines_before = self.env['account.analytic.line'].search([
            ('product_id', '=', product.id),
            ('account_id', '=', self.analytic_account.id),
        ])

        self._product_change_qty(product, 10, self.analytic_account)

        # Checks that there exists an inventory line created with that account,
        # and which belongs to an inventory adjustment that has been validated.
        inventory_lines_after = self.env['stock.inventory.line'].search([
            ('product_id', '=', product.id),
            ('analytic_account_id', '=', self.analytic_account.id),
        ])
        self.assertNotEqual(inventory_lines_before, inventory_lines_after)
        inventory_line_created = inventory_lines_after - inventory_lines_before
        self.assertEqual(inventory_line_created.inventory_id.state, 'done')

        # Checks that there exists two analytic lines created with that account
        analytic_lines_after = self.env['account.analytic.line'].search([
            ('product_id', '=', product.id),
            ('account_id', '=', self.analytic_account.id),
        ])
        self.assertNotEqual(analytic_lines_before, analytic_lines_after)
        analytic_lines_created = analytic_lines_after - analytic_lines_before
        self.assertEqual(sorted(analytic_lines_created.mapped('amount')),
                         [-1000.0, +1000.0])
        self.assertEqual(analytic_lines_created.mapped('unit_amount'),
                         [10.0, 10.0])
