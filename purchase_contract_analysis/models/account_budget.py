# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, exceptions, _


class AccountBudget(models.Model):
    _inherit = "crossovered.budget"

    total = fields.Float(string="Total")

    @api.multi
    def _budget_planned_amount_lines_total(self):
        for budget in self:
            planned_amout_total = 0.0
            for budget_line in budget.crossovered_budget_line:
                planned_amout_total += budget_line.planned_amount
            return planned_amout_total


class AccountBudgetLine(models.Model):
    _inherit = "crossovered.budget.lines"

    @api.depends('general_budget_id')
    @api.multi
    def _verify_budget_lines_budgetary_position(self):
        teste = self.env['crossovered.budget.lines'].search(
            [
                ('general_budget_id', '=', self.general_budget_id.id),
                ('analytic_account_id', '=', self.analytic_account_id.id)
            ]
        )
        self.contracts_budget_lines = teste

    allocated_amount = fields.Float(string="Allocated Amount")
    contracts_budget_lines = fields.One2many(
        comodel_name='crossovered.budget.lines',
        inverse_name='budget_lines_id',
        string='Contracts Budget Lines',
        compute='_verify_budget_lines_budgetary_position'
    )
    budget_lines_id = fields.Many2one(
        string=u'Budget Lines',
        comodel_name='crossovered.budget.lines',
    )

    @api.model
    def create(self, vals):
        budget_id = self.env['crossovered.budget'].browse(
            vals['crossovered_budget_id']
        )
        planned_amount_total = budget_id._budget_planned_amount_lines_total()
        planned_amount_total += vals['planned_amount']
        if budget_id.total and planned_amount_total > budget_id.total:
            raise exceptions.Warning(
                _(
                    "The sum of the Planned amount of the lines "
                    "can't surpass the Budget's total!"
                )
            )
        return super(AccountBudgetLine, self).create(vals)
