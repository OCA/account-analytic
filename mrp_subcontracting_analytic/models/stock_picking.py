# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _prepare_subcontract_mo_vals(self, subcontract_move, bom):
        vals = super()._prepare_subcontract_mo_vals(subcontract_move, bom)
        vals["analytic_distribution"] = subcontract_move.analytic_distribution
        return vals
