# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import _, api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    # NOTE: https://github.com/odoo/odoo/issues/45995
    currency_id = fields.Many2one(
        related='account_id.currency_id',
    )
    user_currency_id = fields.Many2one(
        comodel_name='res.currency',
        compute='_compute_user_currency_id',
    )
    user_amount = fields.Monetary(
        currency_field='user_currency_id',
        compute='_compute_user_amount',
    )

    @api.multi
    def _compute_user_currency_id(self):
        for aal in self:
            aal.user_currency_id = self.env.user.company_id.currency_id

    @api.multi
    @api.depends('amount', 'currency_id', 'company_id')
    def _compute_user_amount(self):
        today = fields.Date.today()
        for aal in self:
            aal.user_amount = aal.currency_id._convert(
                aal.amount,
                aal.user_currency_id,
                aal.company_id,
                today
            )

    @api.model
    def fields_view_get(self,
                        view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super().fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu,
        )

        if view_type == 'tree':
            currency = self.env.user.company_id.currency_id
            view = etree.XML(res['arch'])

            user_amount_field = view.find(".//field[@name='user_amount']")
            if user_amount_field is not None:
                user_amount_field.set('string', _('Amount\u00A0(%s)') % (
                    currency.name,
                ))

            res['arch'] = etree.tostring(
                view,
                encoding='unicode',
            ).replace('\t', '')

        return res
