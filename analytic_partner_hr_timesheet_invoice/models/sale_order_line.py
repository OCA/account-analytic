# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza, Luis M. Ontalba
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _compute_analytic(self, domain=None):
        """Split by partner of the lines to filter only affected analytic
        lines.
        """
        for partner in self.mapped('order_partner_id'):
            so_lines = self.filtered(lambda x: x.order_partner_id == partner)
            if not domain:
                domain = [('so_line', 'in', self.ids), '|',
                          ('amount', '<=', 0.0), ('project_id', '!=', False)]
            partner_domain = list(domain)  # make a copy of the domain
            partner_domain += [
                '|',
                ('other_partner_id', '=', partner.id),
                ('other_partner_id', '=', False),
                '|',
                ('partner_id', '=', partner.id),
                ('partner_id', '=', False),
            ]
            super(SaleOrderLine, so_lines)._compute_analytic(
                domain=partner_domain,
            )
