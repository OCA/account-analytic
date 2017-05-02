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
