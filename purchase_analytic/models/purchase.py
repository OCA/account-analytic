# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "analytic.mixin"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        # To be consistent with order_line readonly behavior
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )

    @api.depends("order_line.analytic_distribution")
    def _compute_analytic_distribution(self):
        """If all order line have same analytic distribution set analytic_distribution.
        If no lines, respect value given by the user.
        """
        for po in self:
            if po.order_line:
                al = po.order_line[0].analytic_distribution or False
                for ol in po.order_line:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                po.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """When set analytic_distribution set analytic distribution on all order lines"""
        for po in self:
            if po.analytic_distribution:
                po.order_line.write({"analytic_distribution": po.analytic_distribution})

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When change analytic_distribution set analytic distribution on all order lines"""
        if self.analytic_distribution:
            self.order_line.update(
                {"analytic_distribution": self.analytic_distribution}
            )
