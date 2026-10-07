from odoo import api, fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "analytic.mixin"]

    analytic_distribution = fields.Json(inverse="_inverse_analytic_distribution")

    @api.depends("order_line.analytic_distribution")
    def _compute_analytic_distribution(self):
        """If all lines have the same analytic distribution, set it on the order.

        If no lines exist, respect the value given by the user.
        """
        for so in self:
            if so.order_line:
                al = so.order_line[0].analytic_distribution or False
                for ol in so.order_line:
                    if ol.analytic_distribution != al:
                        al = False
                        break
                so.analytic_distribution = al

    def _inverse_analytic_distribution(self):
        """When setting the analytic distribution`, apply it to all order lines."""
        for so in self:
            if so.analytic_distribution:
                so.order_line.write({"analytic_distribution": so.analytic_distribution})

    @api.onchange("analytic_distribution")
    def _onchange_analytic_distribution(self):
        """When changing the analytic distribution, apply it to all order lines."""
        if self.analytic_distribution:
            self.order_line.update(
                {"analytic_distribution": self.analytic_distribution}
            )
