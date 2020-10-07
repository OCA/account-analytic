# Copyright 2020 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name,
                         origin, values, bom):
        res = super()._prepare_mo_vals(product_id, product_qty, product_uom,
                                       location_id, name, origin, values, bom)
        if 'account_analytic_id' in values:
            res.update(dict(analytic_account_id=values['account_analytic_id']))
        return res
