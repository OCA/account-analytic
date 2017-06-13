# -*- coding: utf-8 -*-
# Copyright 2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# Copyright 2016 Antiun Ingeniería S.L. - Javier Iniesta
# Copyright 2017 Tecnativa - Luis Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Income Analytic Account',
        company_dependent=True)
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Expense Analytic Account',
        company_dependent=True)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    income_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Income Analytic Account',
        company_dependent=True)
    expense_analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Expense Analytic Account',
        company_dependent=True)
