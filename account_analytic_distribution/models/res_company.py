# -*- coding: utf-8 -*-
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    force_percent = fields.Boolean(
        default=False,
        help="If checked, the sum of all percents of the analytic accounts in "
             "a distribution of this company must be 100%.",
    )
