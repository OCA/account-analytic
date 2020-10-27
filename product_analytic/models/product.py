# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Income Analytic Account',
        company_dependent=True)
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Expense Analytic Account',
        company_dependent=True)
    income_analytic_tag_id = fields.Many2one(
        'account.analytic.tag',
        string='Income Analytic Tag',
        company_dependent=True,
    )
    expense_analytic_tag_id = fields.Many2one(
        'account.analytic.tag',
        string='Expense Analytic Tag',
        company_dependent=True,
    )

    @api.multi
    def _get_product_analytic_accounts(self):
        self.ensure_one()
        return {
            'income': self.income_analytic_account_id or
            self.categ_id.get_income_analytic_account(),
            'expense': self.expense_analytic_account_id or
            self.categ_id.get_expense_analytic_account()
        }

    @api.multi
    def _get_product_analytic_tag(self):
        self.ensure_one()
        return {
            'income': self.income_analytic_tag_id
            or self.categ_id.get_income_analytic_tag(),
            'expense': self.expense_analytic_tag_id
            or self.categ_id.get_expense_analytic_tag(),
        }


class ProductCategory(models.Model):
    _inherit = 'product.category'

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Income Analytic Account',
        company_dependent=True)
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Expense Analytic Account',
        company_dependent=True)
    income_analytic_tag_id = fields.Many2one(
        'account.analytic.tag',
        string='Income Analytic Tag',
        company_dependent=True,
    )
    expense_analytic_tag_id = fields.Many2one(
        'account.analytic.tag',
        string='Expense Analytic Tag',
        company_dependent=True,
    )

    def get_income_analytic_tag(self):
        self.ensure_one()
        if not self.income_analytic_tag_id and self.parent_id:
            return self.parent_id.get_income_analytic_tag()
        return self.income_analytic_tag_id

    def get_expense_analytic_tag(self):
        self.ensure_one()
        if not self.expense_analytic_tag_id and self.parent_id:
            return self.parent_id.get_expense_analytic_tag()
        return self.expense_analytic_tag_id

    def get_income_analytic_account(self):
        self.ensure_one()
        if not self.income_analytic_account_id and self.parent_id:
            return self.parent_id.get_income_analytic_account()
        return self.income_analytic_account_id

    def get_expense_analytic_account(self):
        self.ensure_one()
        if not self.expense_analytic_account_id and self.parent_id:
            return self.parent_id.get_expense_analytic_account()
        return self.expense_analytic_account_id
