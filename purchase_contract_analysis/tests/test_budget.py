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
