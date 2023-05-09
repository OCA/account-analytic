# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockLot(models.Model):
    _name = "stock.lot"
    _inherit = ["stock.lot", "analytic.mixin"]
