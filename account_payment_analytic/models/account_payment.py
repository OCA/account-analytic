from odoo import models


class AccountPayment(models.Model):
    _name = "account.payment"
    _inherit = ["account.payment", "analytic.mixin"]

    def _prepare_move_counterpart_lines(self, default_values):
        line_vals_list = super()._prepare_move_counterpart_lines(default_values)
        if self.analytic_distribution:
            for line_vals in line_vals_list:
                line_vals["analytic_distribution"] = self.analytic_distribution
        return line_vals_list
