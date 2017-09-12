# -*- coding: utf-8 -*-
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _need_procurement(self):
        if self.env.context.get('test_enabled', False):
            return True
        return super(ProductProduct, self)._need_procurement()
