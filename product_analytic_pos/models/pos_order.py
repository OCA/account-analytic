# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _prepare_analytic_account(self, line):
        ana_account_id = super(PosOrder, self)._prepare_analytic_account(line)
        ana_accounts = line.product_id.product_tmpl_id.\
            _get_product_analytic_accounts()
        ana_account_id = ana_accounts['income'].id
        return ana_account_id
