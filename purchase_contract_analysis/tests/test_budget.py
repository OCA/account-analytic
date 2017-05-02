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
        self.budget1.write({'total': 28325})

    def _sum_budget_lines(self, budget):
        total = 0
        for line in budget.crossovered_budget_line:
            total += line.planned_amount
        return total

    def test_budget_total(self):
        "Compare the budget total with the sum of the bugdet lines"
        budget_lines_total = self._sum_budget_lines(self.budget1)
        self.assertEqual(
            self.budget1.total,
            budget_lines_total,
            "Budget total not equal the sum of the budget's line sum"
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
