# Copyright 2011-2020 Akretion - Alexis de Lattre
# Copyright 2016-2020 Camptocamp SA
# Copyright 2020 Druidoo - Iván Todorovich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        res = super()._post(soft=soft)
        self.mapped("line_ids")._check_analytic_required()
        return res
