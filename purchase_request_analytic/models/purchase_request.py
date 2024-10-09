# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _inherit = ["analytic.mixin", "purchase.request"]

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
        help="The default distribution for new lines on this request",
    )

    @api.depends("line_ids.analytic_distribution")
    def _compute_analytic_distribution(self):
        """Take the distribution that is already set on all of our lines."""
        for pr in self:
            al = pr.analytic_distribution
            if pr.line_ids:
                first_line_analytic_distribution = pr.line_ids[0].analytic_distribution
                all_lines_same = all(
                    prl.analytic_distribution == first_line_analytic_distribution
                    for prl in pr.line_ids
                )
                # If all lines share the same analytic_distribution,
                # set it to the purchase request.
                if all_lines_same:
                    pr.analytic_distribution = first_line_analytic_distribution
                    continue
                for prl in pr.line_ids:
                    if prl.analytic_distribution != al:
                        al = False
                        break
            pr.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """Set this requests's distribution on all of its lines."""
        for pr in self.filtered("analytic_distribution"):
            pr.line_ids.analytic_distribution = pr.analytic_distribution
