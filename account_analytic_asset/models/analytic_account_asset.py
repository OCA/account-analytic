# Copyright 2020 Jesus Ramoneda <jesus.ramoneda@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AnalyticAccountAsset(models.Model):
    _inherit = "account.asset.asset"

    account_analytic_id = fields.Many2one(
        comodel_name='account.analytic.account')

    @api.onchange('category_id')
    def onchange_category_id(self):
        res = super(AnalyticAccountAsset, self).onchange_category_id()
        self.account_analytic_id = self.category_id.account_analytic_id
        return res


class AccountAssetLine(models.Model):
    _inherit = "account.asset.depreciation.line"

    @api.multi
    def _set_analytic_account(self):
        def get_move_line(asset_line):
            return 1 if asset_line.asset_id.category_id.type == "sale" else 0
        for rec in self.filtered(
            lambda x: x.move_id and x.asset_id and
                x.asset_id.account_analytic_id):
            i = get_move_line(rec)
            rec.move_id.line_ids[i].analytic_account_id =\
                rec.asset_id.account_analytic_id

    @api.multi
    def write(self, values):
        res = super(AccountAssetLine, self).write(values)
        if values.get('move_id'):
            self._set_analytic_account()
        return res
