# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):

    _name = 'purchase.order.line'
    _inherit = ['analytic.dimension.line', 'purchase.order.line']
    _analytic_tag_field_name = 'analytic_tag_ids'
