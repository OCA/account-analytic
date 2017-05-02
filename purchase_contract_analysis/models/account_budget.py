# -*- coding: utf-8 -*-
# © 2017 KMEE (http://www.kmee.com.br)
# Luiz Felipe do Divino<luiz.divino@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountBudget(models.Model):
    _inherit = "crossovered.budget"

    total = fields.Float(string="Total")


class AccountBudgetLine(models.Model):
    _inherit = "crossovered.budget.lines"

    allocated_amount = fields.Float(string="Allocated Amount")
