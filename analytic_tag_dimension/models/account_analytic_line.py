# Copyright 2017 PESOL (http://pesol.es) - Angel Moya (angel.moya@pesol.es)
# Copyright 2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['analytic.dimension.line', 'account.analytic.line']
    _analytic_tag_field_name = 'tag_ids'
