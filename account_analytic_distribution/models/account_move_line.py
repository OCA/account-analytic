# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_distribution_id = fields.Many2one(
        comodel_name='account.analytic.distribution',
        string='Analytic distribution',
    )

    def _analytic_line_distributed_prepare(self, rule):
        res = self._prepare_analytic_line()
        for line_dict in res:
            amount = (line_dict.get('amount') * rule.percent) / 100.0
            line_dict['amount'] = amount
            line_dict['account_id'] = rule.analytic_account_id.id
        return res and res[0] or False

    @api.multi
    def create_analytic_lines(self):
        super(AccountMoveLine, self).create_analytic_lines()
        for line in self:
            if line.analytic_distribution_id:
                line.analytic_line_ids.unlink()
                for rule in line.analytic_distribution_id.rule_ids:
                    values = line._analytic_line_distributed_prepare(rule)
                    self.env['account.analytic.line'].create(values)
        return True
