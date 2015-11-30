# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Income Analytic Account',
        company_dependent=True,
        domain=[('type', 'not in', ('view', 'template'))])
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Expense Analytic Account',
        company_dependent=True,
        domain=[('type', 'not in', ('view', 'template'))])


class ProductCategory(models.Model):
    _inherit = 'product.category'

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Income Analytic Account',
        company_dependent=True,
        domain=[('type', 'not in', ('view', 'template'))])
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Expense Analytic Account',
        company_dependent=True,
        domain=[('type', 'not in', ('view', 'template'))])
