from odoo import api, fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "analytic.mixin"]

    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    def _get_analytic_order_lines(self):
        return self.order_line.filtered(lambda line: not line.display_type)

    @api.depends("order_line.analytic_distribution", "order_line.display_type")
    def _compute_analytic_distribution(self):
        """If all lines have the same analytic distribution, set it on the order.

        Sections and notes are ignored. If no other lines exist, respect the
        value given by the user.
        """
        for so in self:
            lines = so._get_analytic_order_lines()
            if lines:
                al = lines[0].analytic_distribution or False
                for ol in lines:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                so.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """When setting the analytic distribution, apply it to all order lines."""
        for so in self:
            if so.analytic_distribution:
                so._get_analytic_order_lines().write(
                    {"analytic_distribution": so.analytic_distribution}
                )

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When changing the analytic distribution, apply it to all order lines."""
        if self.analytic_distribution:
            self._get_analytic_order_lines().update(
                {"analytic_distribution": self.analytic_distribution}
            )
