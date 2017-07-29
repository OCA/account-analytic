# -*- coding: utf-8 -*-
# © 2016 Antonio Espinosa - <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AccountAssetAsset(models.Model):
    _inherit = "account.asset.asset"

    def _disposal_line_loss_prepare(self, date, period, journal, loss_account,
                                    loss_value):
        res = super(AccountAssetAsset, self)._disposal_line_loss_prepare(
            date, period, journal, loss_account, loss_value)
        if self.analytic_account_id:
            res['analytic_account_id'] = self.analytic_account_id.id
        return res
