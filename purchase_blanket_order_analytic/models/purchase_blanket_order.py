# Copyright 2026 - TODAY, Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseBlanketOrder(models.Model):
    _name = "purchase.blanket.order"
    _inherit = ["purchase.blanket.order", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        states={
            "done": [("readonly", True)],
            "expired": [("readonly", True)],
        },
    )

    @api.depends("line_ids.analytic_distribution")
    def _compute_analytic_distribution(self):
        """If all order line have same analytic distribution set analytic_distribution.
        If no lines, respect value given by the user.
        """
        for po in self:
            if po.line_ids:
                al = po.line_ids[0].analytic_distribution or False
                for ol in po.line_ids:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                po.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """When set analytic_distribution set analytic distribution on all order lines"""
        for po in self:
            if po.analytic_distribution:
                po.line_ids.write({"analytic_distribution": po.analytic_distribution})

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When change analytic_distribution set analytic distribution on all order lines"""
        if self.analytic_distribution:
            self.line_ids.update({"analytic_distribution": self.analytic_distribution})
