# Copyright 2024 Atte Isopuro <atte.isopuro@avoin.systems>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _get_custom_move_fields(self):
        return super()._get_custom_move_fields() + ["analytic_distribution"]
