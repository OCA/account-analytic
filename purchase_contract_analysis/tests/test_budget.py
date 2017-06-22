# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestBudget(TransactionCase):
    def setUp(self):
        super(TestBudget, self).setUp()
        self.budget1 = self.env.ref(
            'account_budget.crossovered_budget_budgetoptimistic0'
        )
        self.budget1.write({'total': 31325.00})
        self.budget2 = self.env['crossovered.budget'].create(
            {
                'name': '2018-kmee-budget',
                'creating_user_id': self.env.ref('base.user_demo').id,
                'code': 'kmee2018',
                'date_from': '2018-01-01',
                'date_to': '2018-12-31'
            }
        )
        self.purchase_contract1 = self.env['account.analytic.account'].create(
            {
                'name': 'Equipments and Trainning Agrolait Contract',
                'partner_id': self.env.ref('base.res_partner_1').id,
                'manager_id': self.env.ref('base.user_root').id,
                'code': 'AA041',
                'date_start': '2008-04-04'
            }
        )
        self.budget2_line1 = self.env['crossovered.budget.lines'].create(
            {
                'crossovered_budget_id': self.budget2.id,
                'analytic_account_id': self.purchase_contract1.id,
                'general_budget_id': self.env.ref(
                    'account_budget.account_budget_post_purchase0'
                ).id,
                'planned_amount': 550.00,
                'allocated_amount': 450.00,
                'date_from': '2018-01-01',
                'date_to': '2018-12-31'
            }
        )

    def test_new_crossovered_budget_line(self):
        """
        The Creation of a new crossovered budget line can't make the sum of
        the planned amount surpass the budget total
        """
        vals = {
            'crossovered_budget_id': self.budget1.id,
            'analytic_account_id': self.env.ref(
                'account.analytic_consultancy'
            ).id,
            'general_budget_id': self.env.ref(
                'account_budget.account_budget_post_purchase0'
            ).id,
            'date_from': '2007-02-05',
            'date_to': '2017-10-05',
            'planned_amount': 2000,
            'allocated_amount': 1200,
            'practical_amount': 1000,
            'company_id': self.budget1.company_id.id,
        }
        self.assertTrue(
            self.env['crossovered.budget.lines'].create(vals),
            "The sum of the Planned amount surpass the Budget's total after "
            "the creation of this new line!"
        )

    def test_allocated_amount(self):
        """
        Compare if the Allocated Amount field has a value <= Planned Amount and
         >= Pratical Amount
        """
        vals = {
            'crossovered_budget_id': self.budget1.id,
            'analytic_account_id': self.env.ref(
                'account.analytic_consultancy'
            ).id,
            'general_budget_id': self.env.ref(
                'account_budget.account_budget_post_purchase0'
            ).id,
            'date_from': '2007-02-05',
            'date_to': '2017-10-05',
            'planned_amount': 1500,
            'allocated_amount': 1200,
            'practical_amount': 1000,
            'company_id': self.budget1.company_id.id,
        }
        crossovered_budget_line = self.env['crossovered.budget.lines'].create(
            vals
        )
        self.assertTrue(
            crossovered_budget_line.planned_amount >=
            crossovered_budget_line.allocated_amount,
            "Allocated amount can't be bigger than the Planned amount!"
        )
        self.assertTrue(
            crossovered_budget_line.practical_amount <=
            crossovered_budget_line.allocated_amount,
            "Pratical amount can't be bigger than the Allocated amount!"
        )

    def test_verify_all_the_lines_has_the_same_budgetary_position(self):
        """
        Verify if all the linas computed in the 'Contracts Budget Lines' field
        has the same Budgetary Position.
        """
        budget_line_id = self.env.ref(
            'account_budget.crossovered_budget_lines_0'
        )
        budget_line_id._verify_budget_lines_budgetary_position()
        for budget_contract_line in budget_line_id.contracts_budget_lines:
            self.assertEqual(
                budget_contract_line.general_budget_id.id,
                budget_line_id.general_budget_id.id,
                "One or more of the Contracts Budget Lines don't have the "
                "same Budgetary Position as the active Crossovered Budget Line"
            )

    def test_create_contract_purchase_item(self):
        """
        Creation of a new  purchase contract item
        """
        vals = {
            'name': 'Equipments',
            'product_id': self.env.ref('product.product_product_8').id,
            'quantity': 10.0,
            'price': 50.0,
            'expected': 500.0,
            'contract_id': self.purchase_contract1.id,
        }
        self.assertTrue(
            self.env['contract.purchase.itens'].create(vals),
            "Can not create a Purchase contract item correctly!"
        )

    def _create_purchase_order(self, one_purchase_order=None):
        vals = {
            'name': 'Equipments',
            'product_id': self.env.ref('product.product_product_8').id,
            'quantity': 10.0,
            'price': 50.0,
            'contract_id': self.purchase_contract1.id,
            'expected': 500.0,
        }
        self.env['contract.purchase.itens'].create(vals)
        vals = {
            'name': 'Services',
            'product_id': self.env.ref(
                'product.product_product_consultant_product_template'
            ).id,
            'quantity': 5.0,
            'price': 100.0,
            'expected': 500.0,
            'contract_id': self.purchase_contract1.id
        }
        self.env['contract.purchase.itens'].create(vals)
        wizard_id = self.purchase_contract1.create_purchase_orders_wizard()
        wizard = self.env['purchase.order.partial.contract.wizard'].browse(
            wizard_id['res_id']
        )
        if one_purchase_order:
            wizard.all_in_one_purchase_order = True
        product_ids = []
        for line in wizard.line_ids:
            line.quantity = 3
            product_ids.append(line.product_id.id)
        wizard.create_purchase_order()
        purchase_order_lines = self.env['purchase.order.line'].search(
            [
                ('product_id', 'in', product_ids)
            ]
        )
        purchase_order_ids = []
        for line in purchase_order_lines:
            if line.order_id.id not in purchase_order_ids:
                purchase_order_ids.append(line.order_id.id)
        purchase_orders = self.env['purchase.order'].search(
            [
                ('id', 'in', purchase_order_ids),
                ('project_id', '=', self.purchase_contract1.id)
            ]
        )
        return purchase_orders

    def test_create_purchase_order_lines_from_wizard(self):
        """
        Test the creation of the purchase orders from the defined contract
        lines with quantities bigger than 0.
        """
        purchase_orders = self._create_purchase_order()
        self.assertEqual(
            len(purchase_orders),
            2,
            "No purchase order was created or the number of purchase orders "
            "created was differente from the number that had to be(2)!"
        )

    def test_create_one_purchase_order_from_wizard(self):
        """
        Test the creation of the purchase orders from the defined contract
        lines with quantities equal to one.
        """
        purchase_orders = self._create_purchase_order(one_purchase_order=True)
        self.assertEqual(
            len(purchase_orders),
            1,
            "No purchase order was created or the number of purchase orders "
            "created was differente from the number that had to be(1)!"
        )

    def test_planned_amount_bigger_than_budget_total(self):
        """
        Verify if the planned amount of the contracts surpass
        the budget's total
        """
        vals = {
            'crossovered_budget_id': self.budget1.id,
            'analytic_account_id': self.env.ref(
                'account.analytic_consultancy'
            ).id,
            'general_budget_id': self.env.ref(
                'account_budget.account_budget_post_purchase0'
            ).id,
            'date_from': '2007-02-05',
            'date_to': '2017-10-05',
            'planned_amount': 5500,
            'allocated_amount': 3200,
            'practical_amount': 1000,
            'company_id': self.budget1.company_id.id,
        }
        with self.assertRaises(Exception) as context:
            self.env['crossovered.budget.lines'].create(vals)

        self.assertTrue(
            "The sum of the Planned amount of the lines "
            "can't surpass the Budget's total!"
            in context.exception.message
        )

    def test_to_invoice_amount_in_contract_purchase_itens_lines(self):
        """
        Verify if the invoice amount is correct in each line of the contract
        purchase itens lines.
        """
        purchase_orders = self._create_purchase_order()
        for purchase_item_line in \
                self.purchase_contract1.contract_purchase_itens_lines:
            purchase_item_line._compute_to_invoice_amount()
            purchase_orders_item_total = 0.0
            for purchase_order in purchase_orders:
                for line in purchase_order.order_line:
                    if line.product_id.id == purchase_item_line.product_id.id:
                        purchase_orders_item_total += line.price_subtotal
            self.assertEqual(purchase_item_line.to_invoice,
                             purchase_orders_item_total,
                             "To invoice value different from the sum of the"
                             "purchase order lines of that product!")

    def test_invoiced_amount_in_contract_purchase_itens_lines(self):
        """
        Verify if the invoiced amount is correct in each line of the contract
        purchase itens lines
        """
        purchase_orders = self._create_purchase_order()
        purchase_orders[0].wkf_confirm_order()
        purchase_orders[0].action_invoice_create()
        for purchase_item_line in \
                self.purchase_contract1.contract_purchase_itens_lines:
            purchase_item_line._compute_invoiced_amount()
            purchase_invoices_item_total = 0.0
            purchase_order_names = []
            for purchase_order in purchase_orders:
                for line in purchase_order.order_line:
                    if line.product_id.id == purchase_item_line.product_id.id:
                        if purchase_order.name not in purchase_order_names:
                            purchase_order_names.append(purchase_order.name)
            purchase_invoices = self.env['account.invoice'].search(
                [
                    ('origin', 'in', purchase_order_names)
                ]
            )
            for purchase_invoice in purchase_invoices:
                for line in purchase_invoice.invoice_line:
                    if line.product_id.id == purchase_item_line.product_id.id:
                        purchase_invoices_item_total += line.price_subtotal
            self.assertEqual(purchase_item_line.invoiced,
                             purchase_invoices_item_total,
                             "To invoice value different from the sum of the"
                             "purchase order lines of that product!")

    def test_create_contract_purchase_item_wizard(self):
        """
        Test the creation of a contract purchase item by wizard
        """
        wizard_ir = self.purchase_contract1.create_purchase_contract_item()
        self.assertEqual(
            wizard_ir['type'],
            "ir.actions.act_window",
            "Can't create contract purchase item wizard!"
        )
        vals = {
            'name': 'Test Item Wizard',
            'product_id': self.env.ref("product.product_product_9").id,
            'price': 599.00,
            'quantity': 10.00,
            'contract_id': wizard_ir['context']['default_contract_id'],
        }
        wizard_id = self.env[wizard_ir['res_model']].create(vals)
        wizard_id.create_purchase_contract_item()

        self.assertTrue(
            self.env['contract.purchase.itens'].search(
                [('name', '=', 'Test Item Wizard')]),
            "Can't create a purchase contract item with the wizard!"
        )

    def test_back_to_draft(self):
        """
        Test returning contract to draft state
        """
        self.purchase_contract1.set_open()
        self.assertTrue(
            self.purchase_contract1.return_to_draft(),
            "Can't return contract to draft state!"
        )
        purchase_orders = self._create_purchase_order()
        if purchase_orders:
            with self.assertRaises(Exception) as context:
                self.purchase_contract1.return_to_draft()

            self.assertTrue(
                "It's not possible to turn the state of the contract back to "
                "draft because existis purchase orders of this contract!"
                in context.exception.message
            )
