# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    income_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Income Analytic Account",
        company_dependent=True,
    )
    expense_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Expense Analytic Account",
        company_dependent=True,
    )
    income_analytic_account_tag_ids = fields.Many2many(
        string="Income Analytic Tags",
        help="Not company-specific but tags can be company dependent",
        comodel_name="account.analytic.tag",
        relation="product_income_analytic_tag_rel",
    )
    expense_analytic_account_tag_ids = fields.Many2many(
        string="Expense Analytic Tags",
        help="Not company-specific but tags can be company dependent",
        comodel_name="account.analytic.tag",
        relation="product_expense_analytic_tag_rel",
    )

    def _get_product_analytic_accounts(self):
        self.ensure_one()
        return {
            "income": self.income_analytic_account_id
            or self.categ_id.income_analytic_account_id,
            "expense": self.expense_analytic_account_id
            or self.categ_id.expense_analytic_account_id,
        }

    def _get_product_analytic_tags(self):
        self.ensure_one()
        return {
            "income": self.income_analytic_account_tag_ids
            | self.categ_id.income_analytic_account_tag_ids,
            "expense": self.expense_analytic_account_tag_ids
            | self.categ_id.expense_analytic_account_tag_ids,
        }
