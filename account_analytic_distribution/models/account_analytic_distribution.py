# -*- coding: utf-8 -*-
# Copyright 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountAnalyticDistribution(models.Model):
    _name = "account.analytic.distribution"
    _description = "Analytic distribution"
    _order = "name asc"

    @api.model
    def _get_default_company(self):
        m_company = self.env['res.company']
        return m_company._company_default_get('account.analytic.distribution')

    name = fields.Char(
        string='Name',
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=_get_default_company,
    )
    rule_ids = fields.One2many(
        string="Distribution rules",
        comodel_name='account.analytic.distribution.rule',
        inverse_name='distribution_id',
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)',
         _('Distribution name must be unique per Company!')),
    ]

    @api.multi
    @api.constrains('rule_ids')
    def _check_rule_ids(self):
        for distribution in self:
            if not self.env.user.company_id.force_percent:
                continue
            total = sum(distribution.rule_ids.mapped('percent'))
            if total != 100.00:
                raise ValidationError(_("Rules percent doesn't sum 100%"))


class AccountAnalyticDistributionRule(models.Model):
    _name = "account.analytic.distribution.rule"
    _description = "Analytic distribution rule"
    _order = "sequence asc"

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    distribution_id = fields.Many2one(
        string="Distribution",
        required=True,
        comodel_name='account.analytic.distribution',
    )
    percent = fields.Float(
        string="Percentage",
        required=True,
    )
    analytic_account_id = fields.Many2one(
        string="Analytic account",
        comodel_name='account.analytic.account',
    )

    _sql_constraints = [
        ('percent_positive', 'CHECK(percent > 0)',
         _('Percentage must be positive!')),
        ('percent_limit', 'CHECK(percent <= 100)',
         _('Percentage must less or equal 100%!')),
        ('analytic_uniq', 'unique(distribution_id, analytic_account_id)',
         _('Analytic account must be unique per distribution!')),
    ]
