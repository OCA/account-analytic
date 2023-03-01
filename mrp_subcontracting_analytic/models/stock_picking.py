# Copyright 2023 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # pylint: disable=W8110
    def _subcontracted_produce(self, subcontract_details):
        # extending _prepare_subcontract_mo_vals() to pass the analytic distribution to
        # production would cause unexpected result (production moves get duplicated),
        # therefore, instead, we trigger the inverse method upon creation of the
        # subcontracted production.
        super()._subcontracted_produce(subcontract_details)
        self.ensure_one()
        for move, _bom in subcontract_details:
            move._inverse_analytic_distribution()
